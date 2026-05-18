"""Top-level normalization orchestration.

The single public entry-point :func:`normalize` walks the parsed
:class:`UrlParts` through a fixed pipeline (scheme → authority → path
→ query → fragment), applying optional rules from these keyword args:

- ``strip_default_port`` (default ``True``) — drop the port when it
  matches the scheme's default (``http``→80, ``https``→443, ``ws``→80,
  ``wss``→443, ``ftp``→21, etc., per :data:`DEFAULT_PORTS`).
- ``strip_fragment`` (default ``False``) — discard the ``#...`` tail.
- ``sort_query`` (default ``False``) — stable-sort query pairs by key.
- ``remove_dots`` (default ``True``) — apply RFC-3986 §5.2.4
  dot-segment removal to the path.
- ``default_scheme`` (default ``None``) — when the input has no
  scheme, attach this scheme before the rest of the pipeline runs.

:func:`equivalent` is a convenience wrapper that compares the
normalized forms of two URLs under the same options.
"""

from __future__ import annotations

from typing import Optional

from ._errors import UrlNormError
from ._parse import parse, unparse
from ._parts import UrlParts
from ._path import remove_dot_segments
from ._pct import canonicalize
from ._query import canonicalize_query

DEFAULT_PORTS: dict[str, int] = {
    "http": 80,
    "https": 443,
    "ws": 80,
    "wss": 443,
    "ftp": 21,
    "gopher": 70,
    "nntp": 119,
    "ldap": 389,
    "ldaps": 636,
    "telnet": 23,
}


def normalize(
    url: str,
    *,
    strip_default_port: bool = True,
    strip_fragment: bool = False,
    sort_query: bool = False,
    remove_dots: bool = True,
    default_scheme: Optional[str] = None,
) -> str:
    """Return the canonical string form of *url*. See module docstring for options."""
    parts = parse(url)
    parts = _attach_default_scheme(parts, default_scheme)
    parts = _normalize_scheme(parts)
    parts = _normalize_authority(parts, strip_default_port)
    parts = _normalize_path(parts, remove_dots)
    parts = _normalize_query(parts, sort_query)
    parts = _normalize_fragment(parts, strip_fragment)
    return unparse(parts)


def equivalent(a: str, b: str, **opts: object) -> bool:
    """Return True if *a* and *b* normalize to the same string."""
    return normalize(a, **opts) == normalize(b, **opts)  # type: ignore[arg-type]


def _attach_default_scheme(parts: UrlParts, scheme: Optional[str]) -> UrlParts:
    """If parts has no scheme and a default is given, attach it."""
    if scheme is None or parts.scheme:
        return parts
    if not _is_valid_scheme(scheme):
        raise UrlNormError(f"invalid default_scheme: {scheme!r}")
    return parts.replace(scheme=scheme)


def _is_valid_scheme(scheme: str) -> bool:
    """Lightweight scheme validator."""
    if not scheme or not scheme[0].isalpha():
        return False
    return all(c.isalnum() or c in "+-." for c in scheme)


def _normalize_scheme(parts: UrlParts) -> UrlParts:
    """Lower-case the scheme name."""
    if not parts.scheme:
        return parts
    return parts.replace(scheme=parts.scheme.lower())


def _normalize_authority(parts: UrlParts, strip_default_port: bool) -> UrlParts:
    """Lower-case the host, canonicalize userinfo, strip default ports."""
    if not parts.has_authority:
        return parts
    host = _normalize_host(parts.host)
    userinfo = canonicalize(parts.userinfo)
    port = parts.port
    if strip_default_port and port is not None:
        if DEFAULT_PORTS.get(parts.scheme) == port:
            port = None
    return parts.replace(host=host, userinfo=userinfo, port=port)


def _normalize_host(host: str) -> str:
    """Lower-case a host, preserving IPv6 bracket structure."""
    if host.startswith("[") and host.endswith("]"):
        return "[" + host[1:-1].lower() + "]"
    return host.lower()


def _normalize_path(parts: UrlParts, remove_dots: bool) -> UrlParts:
    """Canonicalize percent-encoding and (optionally) remove dot segments."""
    path = canonicalize(parts.path)
    if remove_dots:
        path = remove_dot_segments(path)
    if parts.has_authority and not path:
        path = "/"
    return parts.replace(path=path)


def _normalize_query(parts: UrlParts, sort_query: bool) -> UrlParts:
    """Canonicalize percent-encoding in the query, optionally sorting it."""
    if not parts.query:
        return parts
    return parts.replace(query=canonicalize_query(parts.query, sort=sort_query))


def _normalize_fragment(parts: UrlParts, strip_fragment: bool) -> UrlParts:
    """Strip or canonicalize the fragment."""
    if strip_fragment:
        return parts.replace(fragment="")
    if not parts.fragment:
        return parts
    return parts.replace(fragment=canonicalize(parts.fragment))
