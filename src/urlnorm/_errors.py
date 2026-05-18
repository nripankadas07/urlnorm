"""Public exception type for urlnorm."""

from __future__ import annotations


class UrlNormError(ValueError):
    """Raised when a URL cannot be parsed or normalized.

    Subclasses :class:`ValueError` so callers can use either name.
    """
