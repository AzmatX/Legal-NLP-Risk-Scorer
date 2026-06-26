"""
Clause segmentation service.
Splits contract text into individual clauses based on headings, numbering, and legal patterns.
"""
import re
from dataclasses import dataclass
from typing import List, Optional, Pattern

@dataclass
class Clause:
    heading: Optional[str]
    text: str
    start_char: int
    end_char: int
    level: int = 0

    def __repr__(self) -> str:
        return f"<Clause heading={self.heading!r} len={len(self.text)}>"


DEFAULT_PATTERNS = {
    "article": re.compile(
        r'^(ARTICLE|ART)\s+([IVXLCDM]+|\d+(?:\.\d+)*)\s*[-–:.]?\s*(.*)$',
        re.IGNORECASE | re.MULTILINE
    ),
    "section": re.compile(
        r'^(Section|Sect\.|§)\s+(\d+(?:\.\d+)*)\s*[-–:.]?\s*(.*)$',
        re.IGNORECASE | re.MULTILINE
    ),
    "numbered": re.compile(
        r'^(\d+(?:\.\d+)*|\w\)|[\(（]\w[\)）]|[IVXLCDM]+\.)\s+(.*)$',
        re.MULTILINE
    ),
    "preamble": re.compile(
        r'^(WHEREAS|NOW\s+THEREFORE|THEREFORE|WHEREFORE)\b',
        re.IGNORECASE | re.MULTILINE
    ),
    "short_heading": re.compile(
        r'^([A-Z][A-Z\s]+[A-Z])\s*[:.]\s*(.*)$',
        re.MULTILINE
    ),
}


class ClauseSegmenter:
    def __init__(self, patterns: Optional[dict] = None):
        self.patterns = patterns or DEFAULT_PATTERNS

    def segment(self, text: str) -> List[Clause]:
        if not text or not text.strip():
            return []

        lines = text.splitlines(keepends=False)
        clauses = []
        current_heading = None
        current_text_lines = []
        current_start = 0
        current_end = 0

        i = 0
        while i < len(lines):
            line = lines[i]
            heading, is_heading = self._detect_heading(line)
            if is_heading:
                if current_text_lines:
                    clauses.append(self._build_clause(
                        current_heading,
                        current_text_lines,
                        current_start,
                        current_end
                    ))
                current_heading = heading
                current_text_lines = [line]
                current_start = self._get_line_start(text, i, lines)
                current_end = self._get_line_end(text, i, lines)
            else:
                if not current_text_lines:
                    current_heading = None
                    current_text_lines = [line]
                    current_start = self._get_line_start(text, i, lines)
                    current_end = self._get_line_end(text, i, lines)
                else:
                    current_text_lines.append(line)
                    current_end = self._get_line_end(text, i, lines)
            i += 1

        if current_text_lines:
            clauses.append(self._build_clause(
                current_heading,
                current_text_lines,
                current_start,
                current_end
            ))
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

        if line_stripped.isupper() and len(line_stripped.split()) <= 10:
            return line_stripped, True
        return None, False

    def _build_clause(self, heading: Optional[str], lines: List[str],
                      start_char: int, end_char: int) -> Clause:
        text = "\n".join(lines)
        return Clause(
            heading=heading,
            text=text,
            start_char=start_char,
            end_char=end_char,
        )

    def _get_line_start(self, full_text: str, line_idx: int, lines: List[str]) -> int:
        if line_idx == 0:
            return 0
        prev_len = sum(len(l) + 1 for l in lines[:line_idx])
        return prev_len

    def _get_line_end(self, full_text: str, line_idx: int, lines: List[str]) -> int:
        start = self._get_line_start(full_text, line_idx, lines)
        return start + len(lines[line_idx])


def segment_contract(text: str) -> List[Clause]:
    segmenter = ClauseSegmenter()
    return segmenter.segment(text)