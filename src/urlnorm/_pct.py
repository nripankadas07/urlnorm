"""Percent-encoding canonicalization helpers.

Two rules from RFC 3986:

1. Hex digits must be upper-case (``%2f`` → ``%2F``).
2. Encoded unreserved characters MUST be decoded (``%41`` → ``A``).

The unreserved set is ``ALPHA / DIGIT / "-" / "." / "_" / "~"`` (§2.3).
"""

from __future__ import annotations

_HEX = set("0123456789abcdefABCDEF")
_UNRESERVED = set(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789-._~"
)


def _looks_like_pct(text: str, idx: int) -> bool:
    """Return True if ``text[idx:idx+3]`` is a valid percent-triplet."""
    return (
        idx + 2 < len(text)
        and text[idx] == "%"
        and text[idx + 1] in _HEX
        and text[idx + 2] in _HEX
    )


def canonicalize(text: str) -> str:
    """Canonicalize percent-encoding in *text*.

    Bare ``%`` characters that are not followed by two hex digits are left
    alone. Any malformed encodings round-trip unchanged.
    """
    out: list[str] = []
    i = 0
    while i < len(text):
        if not _looks_like_pct(text, i):
            out.append(text[i])
            i += 1
            continue
        decoded = chr(int(text[i + 1 : i + 3], 16))
        if decoded in _UNRESERVED:
            out.append(decoded)
        else:
            out.append("%" + text[i + 1 : i + 3].upper())
        i += 3
    return "".join(out)
