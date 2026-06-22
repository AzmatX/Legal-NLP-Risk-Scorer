"""
Enhanced Text Cleaner for Legal Contract Documents.

This module provides advanced text cleaning capabilities specifically designed
for legal contracts, preserving important legal terminology while removing
noise such as headers, footers, page numbers, and special characters.
"""

import re


class TextCleaner:
    """
    Advanced text cleaner for legal documents.

    Preserves legal terminology while removing noise like:
    - Headers and footers
    - Page numbers
    - Special characters (except legal symbols)
    - Extra whitespace
    - Watermarks
    """

    # Legal symbols and characters to preserve
    LEGAL_SYMBOLS = {
        '§', '¶', '©', '®', '™', '°', '±', '×', '÷',
        '$', '€', '£', '¥', '¢', '%', '&', '@', '#',
        '—', '–', '…', '"', "'", '`', '"'
    }

    # Common header/footer patterns to remove
    HEADER_FOOTER_PATTERNS = [
        r'^Page\s+\d+\s*of\s*\d+',  # "Page X of Y"
        r'^\d+\s*of\s*\d+',  # "X of Y"
        r'^Page\s+\d+',  # "Page X"
        r'^CONFIDENTIAL.*?$',  # Confidential watermarks
        r'^DRAFT.*?$',  # Draft watermarks
        r'^ATTORNEY\s+CLIENT\s+PRIVILEGED.*?$',  # Privilege notices
        r'^WORK\s+PRODUCT.*?$',  # Work product notices
        r'^©\s+\d{4}.*?$',  # Copyright lines at page boundaries
        r'^All\s+Rights\s+Reserved.*?$',  # Rights reserved
    ]

    # Patterns to normalize but not remove
    NORMALIZE_PATTERNS = {
        r'\n{3,}': '\n\n',  # Multiple newlines to double
        r' {2,}': ' ',  # Multiple spaces to single
        r'\t+': ' ',  # Tabs to space
        r' +\n': '\n',  # Trailing spaces before newline
        r'\n +': '\n',  # Leading spaces after newline
    }

    # Legal terms that should never be lowercased
    PRESERVE_CASE_TERMS = [
        'CEO', 'CFO', 'COO', 'CTO', 'CIO',
        'LLC', 'Inc', 'Corp', 'Ltd', 'LP', 'LLP',
        'USA', 'UK', 'EU', 'US', 'CA', 'NY',
        'SEC', 'GDPR', 'HIPAA', 'SOX',
        'Exhibit', 'Appendix', 'Schedule', 'Article', 'Section',
        'Party A', 'Party B', 'Licensor', 'Licensee',
        'Buyer', 'Seller', 'Lessee', 'Lessor'
    ]

    def __init__(self,
                 lowercase: bool = False,
                 remove_headers_footers: bool = True,
                 preserve_legal_symbols: bool = True,
                 min_word_length: int = 1):
        """
        Initialize the text cleaner.

        Args:
            lowercase: Whether to convert text to lowercase (default: False)
            remove_headers_footers: Whether to detect and remove headers/footers
            preserve_legal_symbols: Whether to preserve legal symbols
            min_word_length: Minimum word length to keep (filters noise)
        """
        self.lowercase = lowercase
        self.remove_headers_footers = remove_headers_footers
        self.preserve_legal_symbols = preserve_legal_symbols
        self.min_word_length = min_word_length

        # Compile regex patterns
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for efficiency."""
        self.header_footer_regex = [
            re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            for pattern in self.HEADER_FOOTER_PATTERNS
        ]

        self.normalize_patterns = {
            re.compile(pattern): replacement
            for pattern, replacement in self.NORMALIZE_PATTERNS.items()
        }

    def clean(self, text: str) -> str:
        """
        Clean contract text while preserving legal terminology.

        Args:
            text: Raw text from OCR or PDF extraction

        Returns:
            Cleaned text suitable for NLP processing
        """
        if not text or not text.strip():
            return ""

        # Step 1: Remove headers and footers if enabled
        if self.remove_headers_footers:
            text = self._remove_headers_footers(text)

        # Step 2: Normalize whitespace and formatting
        text = self._normalize_whitespace(text)

        # Step 3: Handle case conversion carefully
        if self.lowercase:
            text = self._smart_lowercase(text)

        # Step 4: Remove special characters (preserving legal symbols)
        if self.preserve_legal_symbols:
            text = self._remove_special_chars_preserve_legal(text)
        else:
            text = self._remove_special_chars(text)

        # Step 5: Filter very short words (likely noise)
        text = self._filter_short_words(text)

        # Step 6: Final cleanup
        text = text.strip()

        return text

    def _remove_headers_footers(self, text: str) -> str:
        """Remove common header and footer patterns."""
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            is_header_footer = False

            for pattern in self.header_footer_regex:
                if pattern.match(line.strip()):
                    is_header_footer = True
                    break

            if not is_header_footer:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace and line breaks."""
        for pattern, replacement in self.normalize_patterns.items():
            text = pattern.sub(replacement, text)

        return text

    def _smart_lowercase(self, text: str) -> str:
        """
        Convert to lowercase while preserving important legal terms.

        Args:
            text: Input text

        Returns:
            Text with selective lowercasing
        """
        result = text

        for term in self.PRESERVE_CASE_TERMS:
            # Temporarily replace preserved terms with placeholders
            placeholder = f"__PRESERVE_{hash(term) % 100000}__"
            result = result.replace(term, placeholder)

        # Lowercase the rest
        result = result.lower()

        # Restore preserved terms
        for term in self.PRESERVE_CASE_TERMS:
            placeholder = f"__PRESERVE_{hash(term) % 100000}__"
            result = result.replace(placeholder, term)

        return result

    def _remove_special_chars_preserve_legal(self, text: str) -> str:
        """
        Remove special characters while preserving legal symbols.

        Args:
            text: Input text

        Returns:
            Text with non-legal special characters removed
        """
        # Keep alphanumeric, whitespace, and legal symbols
        allowed_chars = set(
            'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
            '0123456789'
            ' \n\t'
        )
        allowed_chars.update(self.LEGAL_SYMBOLS)

        return ''.join(char if char in allowed_chars else ' ' for char in text)

    def _remove_special_chars(self, text: str) -> str:
        """Remove all special characters."""
        return re.sub(r'[^\w\s]', ' ', text)

    def _filter_short_words(self, text: str) -> str:
        """
        Filter out very short words that are likely noise.

        Preserves single-letter legal terms like 'A' in 'Party A'.
        """
        words = text.split()
        filtered_words = []

        for word in words:
            # Keep if long enough or is a single letter followed by period
            if len(word) >= self.min_word_length:
                filtered_words.append(word)
            elif len(word) == 1 and word.isalpha():
                # Check if it might be part of a party designation
                filtered_words.append(word)

        return ' '.join(filtered_words)

    def clean_batch(self, texts: list[str]) -> list[str]:
        """
        Clean multiple texts efficiently.

        Args:
            texts: List of texts to clean

        Returns:
            List of cleaned texts
        """
        return [self.clean(text) for text in texts]

    def extract_clean_sections(
        self,
        text: str,
        section_markers: list[str] | None = None
    ) -> dict[str, str]:
        """
        Extract and clean specific sections from a contract.

        Args:
            text: Full contract text
            section_markers: Optional list of section marker strings

        Returns:
            Dictionary mapping section names to cleaned text
        """
        if section_markers is None:
            section_markers = [
                'ARTICLE', 'SECTION', 'CLAUSE', 'PART',
                '§', 'Exhibit', 'Appendix', 'Schedule'
            ]

        sections = {}
        current_section = "introduction"
        current_text = []

        lines = text.split('\n')

        for line in lines:
            is_section_start = False

            for marker in section_markers:
                if line.strip().upper().startswith(marker.upper()):
                    # Save previous section
                    if current_text:
                        sections[current_section] = self.clean('\n'.join(current_text))

                    # Start new section
                    current_section = line.strip()[:100]  # Limit section name length
                    current_text = []
                    is_section_start = True
                    break

            if not is_section_start:
                current_text.append(line)

        # Don't forget the last section
        if current_text:
            sections[current_section] = self.clean('\n'.join(current_text))

        return sections
