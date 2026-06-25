"""
Enhanced Text Cleaner for Legal Contract Documents.

This module provides advanced text cleaning capabilities specifically designed
for legal contracts, preserving important legal terminology while removing
noise such as headers, footers, page numbers, and special characters.
"""

import re
from re import Pattern


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
    LEGAL_SYMBOLS: set[str] = {
        '§', '¶', '©', '®', '™', '°', '±', '×', '÷',
        '$', '€', '£', '¥', '¢', '%', '&', '@', '#',
        '—', '–', '…', '"', "'", '`', '"'
    }

    # Common header/footer patterns to remove (as strings, will be combined)
    HEADER_FOOTER_PATTERNS = [
        r'Page\s+\d+\s*of\s*\d+',            # "Page X of Y"
        r'\d+\s*of\s*\d+',                   # "X of Y"
        r'Page\s+\d+',                       # "Page X"
        r'CONFIDENTIAL.*?',                  # Confidential watermarks
        r'DRAFT.*?',                         # Draft watermarks
        r'ATTORNEY\s+CLIENT\s+PRIVILEGED.*?',# Privilege notices
        r'WORK\s+PRODUCT.*?',               # Work product notices
        r'©\s+\d{4}.*?',                     # Copyright lines
        r'All\s+Rights\s+Reserved.*?',       # Rights reserved
    ]

    # Patterns to normalize but not remove
    NORMALIZE_PATTERNS: dict[str, str] = {
        r'\n{3,}': '\n\n',            # Multiple newlines to double
        r' {2,}': ' ',               # Multiple spaces to single
        r'\t+': ' ',                 # Tabs to space
        r' +\n': '\n',              # Trailing spaces before newline
        r'\n +': '\n',              # Leading spaces after newline
    }

    # Legal terms that should never be lowercased
    PRESERVE_CASE_TERMS: list[str] = [
        'CEO', 'CFO', 'COO', 'CTO', 'CIO',
        'LLC', 'Inc', 'Corp', 'Ltd', 'LP', 'LLP',
        'USA', 'UK', 'EU', 'US', 'CA', 'NY',
        'SEC', 'GDPR', 'HIPAA', 'SOX',
        'Exhibit', 'Appendix', 'Schedule', 'Article', 'Section',
        'Party A', 'Party B', 'Licensor', 'Licensee',
        'Buyer', 'Seller', 'Lessee', 'Lessor'
    ]

    # ----- Pre‑computed attributes for speed and safety -----
    # Allowed character set for preserve mode (built once)
    _allowed_chars_preserve: set[str] = set()
    # Combined header/footer regex (built once per instance, but pattern is static)
    _combined_header_footer_regex: Pattern[str] | None = None
    # Placeholder templates for smart lowercasing (unique)
    _placeholder_prefix: str = "__PRESERVE_{}_TOKEN__"

    def __init__(
        self,
        lowercase: bool = False,
        remove_headers_footers: bool = True,
        preserve_legal_symbols: bool = True,
        min_word_length: int = 1
    ):
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

        # Build allowed character set once (if not already done at class level)
        if not TextCleaner._allowed_chars_preserve:
            base_chars = set(
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
                '0123456789'
                ' \n\t'
            )
            base_chars.update(self.LEGAL_SYMBOLS)
            TextCleaner._allowed_chars_preserve = base_chars

        # Build combined header/footer regex once (static across instances)
        if TextCleaner._combined_header_footer_regex is None:
           # Wrap each pattern to match the full stripped line,
            # ignoring case and optional whitespace
            combined = '|'.join(
                rf'(?:{p})' for p in self.HEADER_FOOTER_PATTERNS
            )
            # Anchor to start and end of stripped line (since we strip before matching)
            TextCleaner._combined_header_footer_regex = re.compile(
                rf'^(?:{combined})$',
                re.IGNORECASE
            )

        # Compile normalisation patterns (instance‑level, could be class‑level too)
        self._norm_patterns: dict[Pattern, str] = {
            re.compile(pattern): replacement
            for pattern, replacement in self.NORMALIZE_PATTERNS.items()
        }

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------
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

        # Pre‑compute upper‑case markers for faster comparison
        upper_markers = [m.upper() for m in section_markers]

        sections = {}
        current_section = "introduction"
        current_text: list[str] = []

        lines = text.split('\n')

        for line in lines:
            # Check for section start using uppercase strip once per line
            line_stripped_upper = line.strip().upper()
            is_section_start = False

            for marker_upper in upper_markers:
                if line_stripped_upper.startswith(marker_upper):
                    # Save previous section
                    if current_text:
                        sections[current_section] = self.clean('\n'.join(current_text))

                    # Start new section – use original stripped line (capped length)
                    current_section = line.strip()[:100]
                    current_text = []
                    is_section_start = True
                    break

            if not is_section_start:
                current_text.append(line)

        # Don't forget the last section
        if current_text:
            sections[current_section] = self.clean('\n'.join(current_text))

        return sections

    # ------------------------------------------------------------------
    # Private cleaning steps
    # ------------------------------------------------------------------
    def _remove_headers_footers(self, text: str) -> str:
        """
        Remove common header and footer patterns using a single combined regex.
        """
        lines = text.split('\n')
        kept_lines = []

        for line in lines:
            stripped = line.strip()
            # Check against the combined pattern (full‑line match)
            if not TextCleaner._combined_header_footer_regex.match(stripped):
                kept_lines.append(line)

        return '\n'.join(kept_lines)

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace and line breaks using compiled patterns."""
        for pattern, replacement in self._norm_patterns.items():
            text = pattern.sub(replacement, text)
        return text

    def _smart_lowercase(self, text: str) -> str:
        """
        Convert to lowercase while preserving important legal terms.

        Uses unique, index‑based placeholders to avoid collisions.
        """
        # Replace each term with a unique safe placeholder
        placeholders: list[str] = []
        for i, term in enumerate(self.PRESERVE_CASE_TERMS):
            placeholder = self._placeholder_prefix.format(i)
            placeholders.append(placeholder)
            text = text.replace(term, placeholder)

        # Lowercase everything
        text = text.lower()

        # Restore original terms in the same order
        for i, term in enumerate(self.PRESERVE_CASE_TERMS):
            text = text.replace(placeholders[i], term)

        return text

    def _remove_special_chars_preserve_legal(self, text: str) -> str:
        """
        Remove special characters while preserving legal symbols.

        Uses pre‑computed allowed character set for speed.
        """
        allowed = TextCleaner._allowed_chars_preserve
        return ''.join(char if char in allowed else ' ' for char in text)

    def _remove_special_chars(self, text: str) -> str:
        """Remove all special characters (keeps alphanumeric and whitespace)."""
        return re.sub(r'[^\w\s]', ' ', text)

    def _filter_short_words(self, text: str) -> str:
        """
        Filter out very short words that are likely noise,
        preserving single‑letter legal references like 'A' in 'Party A'.
        """
        words = text.split()
        filtered = []

        for word in words:
            if len(word) >= self.min_word_length or (len(word) == 1 and word.isalpha()):
                filtered.append(word)

        return ' '.join(filtered)