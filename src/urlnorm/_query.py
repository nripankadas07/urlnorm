"""Query-string canonicalization helpers."""

from __future__ import annotations

from ._pct import canonicalize


def split_pairs(query: str) -> list[tuple[str, str | None]]:
    """Split a query string on ``&`` (and ``;``) into ``(key, value)`` pairs.

    A pair with no ``=`` becomes ``(key, None)`` so we can faithfully
    re-serialize a "bare key" form like ``?debug``.
    """
    if not query:
        return []
    pairs: list[tuple[str, str | None]] = []
    for raw in _split_separators(query):
        if raw == "":
            continue
        eq = raw.find("=")
        if eq < 0:
            pairs.append((raw, None))
        else:
            pairs.append((raw[:eq], raw[eq + 1 :]))
    return pairs


def _split_separators(query: str) -> list[str]:
    """Split on ``&`` only; ``;`` is not a separator post-WHATWG."""
    return query.split("&")


def canonicalize_query(query: str, *, sort: bool) -> str:
    """Canonicalize a query string.

    - Each key and value is run through percent-encoding canonicalization.
    - When ``sort`` is true, pairs are sorted by key, then by value with
      ``None`` (key-only) sorting before any string value.
    """
    pairs = split_pairs(query)
    canonical = [_canonicalize_pair(k, v) for k, v in pairs]
    if sort:
        canonical.sort(key=_sort_key)
    return "&".join(_render_pair(k, v) for k, v in canonical)


def _canonicalize_pair(key: str, value: str | None) -> tuple[str, str | None]:
    """Canonicalize a single ``(key, value)`` pair's percent-encoding."""
    new_key = canonicalize(key)
    new_value = canonicalize(value) if value is not None else None
    return new_key, new_value


def _render_pair(key: str, value: str | None) -> str:
    """Render a single query pair, preserving the bare-key form."""
    if value is None:
        return key
    return f"{key}={value}"


def _sort_key(pair: tuple[str, str | None]) -> tuple[str, int, str]:
    """Stable sort key. ``None`` values sort before any string value."""
    key, value = pair
    bucket = 0 if value is None else 1
    return key, bucket, value or ""
