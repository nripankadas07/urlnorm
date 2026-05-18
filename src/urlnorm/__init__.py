"""urlnorm — zero-dependency URL normalizer.

Public API:

- :func:`normalize` — return a canonical URL string.
- :func:`equivalent` — return True if two URLs normalize to the same value.
- :func:`parse` / :func:`unparse` — round-trip a URL through :class:`UrlParts`.
- :class:`UrlParts` — frozen dataclass with the parsed components.
- :class:`UrlNormError` — error type for invalid inputs.

Examples:

    >>> import urlnorm
    >>> urlnorm.normalize("HTTP://Example.com:80/a/./b/../c?b=2&a=1#frag")
    'http://example.com/a/c?b=2&a=1#frag'
    >>> urlnorm.equivalent(
    ...     "https://example.com/p%2fq",
    ...     "https://example.com/p%2Fq",
    ... )
    True
"""

from __future__ import annotations

from ._errors import UrlNormError
from ._norm import DEFAULT_PORTS, equivalent, normalize
from ._parse import parse, unparse
from ._parts import UrlParts

__all__ = [
    "DEFAULT_PORTS",
    "UrlNormError",
    "UrlParts",
    "equivalent",
    "normalize",
    "parse",
    "unparse",
]

__version__ = "0.1.0"
