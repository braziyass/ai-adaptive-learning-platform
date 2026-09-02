from __future__ import annotations

import re


class TextCleaner:
    _whitespace_re = re.compile(r"\s+")
    _hyphen_line_break_re = re.compile(r"(\w)-\s*\n\s*(\w)")

    def clean(self, text: str) -> str:
        if not text:
            return ""
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        normalized = self._hyphen_line_break_re.sub(r"\1\2", normalized)
        normalized = normalized.replace("\n", " ")
        normalized = self._whitespace_re.sub(" ", normalized)
        return normalized.strip()