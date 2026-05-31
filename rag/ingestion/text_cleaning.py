"""Production-grade text normalization for RAG."""

from __future__ import annotations

import re

# Control chars and odd PDF artifacts
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_BULLET_GLYPHS = re.compile(r"[\u2022\u2023\u25e6\u2043\u2219•▪▫◦]")
_NON_INFORMATIVE = re.compile(r"[■□▢▣▤▥▦▧▨▩░▒▓█]+")

# Repeated header/footer lines (same line appearing 3+ times)
_LINE_REPEAT = re.compile(r"^(.{8,80})\n(?:.*\n)*?\1(?:\n.*\n)*?\1", re.MULTILINE)


def clean_text(text: str) -> str:
    """
    Normalize extracted PDF text for chunking and embedding.

    - Removes control characters and decorative glyphs
    - Collapses excessive whitespace
    - Fixes broken line breaks (hyphenation, mid-sentence wraps)
    - Strips likely repeated headers/footers
    """
    if not text:
        return ""

    text = _CONTROL_CHARS.sub("", text)
    text = _BULLET_GLYPHS.sub(" ", text)
    text = _NON_INFORMATIVE.sub(" ", text)

    # Unify line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Fix hyphenated line breaks: "innova-\n tion" -> "innovation"
    text = re.sub(r"(\w)-\n\s*(\w)", r"\1\2", text)

    # Join lines broken mid-sentence (lowercase letter continues)
    text = re.sub(r"([a-z,;])\n([a-z])", r"\1 \2", text)

    # Remove lines that are only page numbers or slide numbers
    lines: list[str] = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        if re.fullmatch(r"\d{1,4}", stripped):
            continue
        if re.fullmatch(r"(page|slide)\s*\d+", stripped, re.IGNORECASE):
            continue
        lines.append(stripped)

    text = "\n".join(lines)
    text = _remove_repeated_lines(text)

    # Collapse whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def _remove_repeated_lines(text: str) -> str:
    """Drop lines that appear many times (likely headers/footers)."""
    lines = text.split("\n")
    if len(lines) < 6:
        return text

    counts: dict[str, int] = {}
    for line in lines:
        key = line.strip().lower()
        if len(key) >= 8:
            counts[key] = counts.get(key, 0) + 1

    repeated = {k for k, v in counts.items() if v >= 3}
    if not repeated:
        return text

    filtered = [
        line
        for line in lines
        if line.strip().lower() not in repeated or len(line.strip()) > 80
    ]
    return "\n".join(filtered)
