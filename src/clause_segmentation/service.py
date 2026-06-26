"""
Clause segmentation service.
Splits contract text into individual clauses based on headings, numbering, and legal patterns.
"""

import re
from dataclasses import dataclass


@dataclass
class Clause:
    heading: str | None
    text: str
    start_char: int
    end_char: int
    level: int = 0

    def __repr__(self) -> str:
        return f"<Clause heading={self.heading!r} len={len(self.text)}>"


DEFAULT_PATTERNS = {
    "article": re.compile(
        r"^(ARTICLE|ART)\s+([IVXLCDM]+|\d+(?:\.\d+)*)\s*[-–:.]?\s*(.*)$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "section": re.compile(
        r"^(Section|Sect\.|§)\s+(\d+(?:\.\d+)*)\s*[-–:.]?\s*(.*)$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "numbered": re.compile(
        r"^(\d+(?:\.\d+)*|\w\)|[\(（]\w[\)）]|[IVXLCDM]+\.)\s+(.*)$",
        re.MULTILINE,
    ),
    "preamble": re.compile(
        r"^(WHEREAS|NOW\s+THEREFORE|THEREFORE|WHEREFORE)\b",
        re.IGNORECASE | re.MULTILINE,
    ),
    "short_heading": re.compile(r"^([A-Z][A-Z\s]+[A-Z])\s*[:.]\s*(.*)$", re.MULTILINE),
}


class ClauseSegmenter:
    def __init__(self, patterns: dict | None = None):
        self.patterns = patterns or DEFAULT_PATTERNS

    def segment(self, text: str) -> list[Clause]:
        """Optimized O(n) segmentation using running character offset."""
        if not text or not text.strip():
            return []

        lines = text.splitlines(keepends=False)
        clauses: list[Clause] = []

        current_heading = None
        current_text_lines: list[str] = []
        current_start = 0
        current_end = 0

        # ✅ Running character offset prevents O(n²) repeated substring scans
        global_pos = 0

        for line in lines:
            line_len = len(line)
            line_start = global_pos
            line_end = global_pos + line_len

            heading, is_heading = self._detect_heading(line)

            if is_heading:
                if current_text_lines:
                    clauses.append(
                        self._build_clause(
                            current_heading,
                            current_text_lines,
                            current_start,
                            current_end,
                        )
                    )

                current_heading = heading
                current_text_lines = [line]
                current_start = line_start
                current_end = line_end

            else:
                if not current_text_lines:
                    # Text starts without a heading
                    current_heading = None
                    current_text_lines = [line]
                    current_start = line_start
                    current_end = line_end
                else:
                    current_text_lines.append(line)
                    current_end = line_end

            # splitlines() removes '\n' — add it back for accurate character offsets
            global_pos += line_len + 1

        # Last clause
        if current_text_lines:
            clauses.append(
                self._build_clause(
                    current_heading,
                    current_text_lines,
                    current_start,
                    current_end,
                )
            )

        return clauses

    def _detect_heading(self, line: str) -> tuple:
        line_stripped = line.strip()
        if not line_stripped:
            return None, False

        for name, pattern in self.patterns.items():
            match = pattern.match(line_stripped)
            if match:
                if name == "article":
                    heading = f"ARTICLE {match.group(2)}"
                    if match.group(3):
                        heading += f": {match.group(3)}"
                    return heading.strip(), True
                elif name == "section":
                    heading = f"Section {match.group(2)}"
                    if match.group(3):
                        heading += f": {match.group(3)}"
                    return heading.strip(), True
                elif name == "numbered":
                    return f"Clause {match.group(1)}", True
                elif name == "preamble":
                    return line_stripped, True
                elif name == "short_heading":
                    return match.group(1), True

        # Catch-all: all-uppercase short lines treated as headings
        if line_stripped.isupper() and len(line_stripped.split()) <= 10:
            return line_stripped, True

        return None, False

    def _build_clause(
        self,
        heading: str | None,
        lines: list[str],
        start_char: int,
        end_char: int,
    ) -> Clause:
        text = "\n".join(lines)
        return Clause(
            heading=heading,
            text=text,
            start_char=start_char,
            end_char=end_char,
        )


# ---------- Convenience function ----------
def segment_contract(text: str) -> list[Clause]:
    """Public API: segment a full contract into clauses."""
    segmenter = ClauseSegmenter()
    return segmenter.segment(text)