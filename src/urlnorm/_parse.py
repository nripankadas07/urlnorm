"""RFC-3986 inspired URL parser.

We hand-roll the parser (no ``urllib.parse``) for predictable, strict
behavior: bracketed IPv6 hosts, mandatory numeric ports, no implicit
scheme detection. The parser only *splits* — it never decodes or
normalizes.
"""

from __future__ import annotations

from ._errors import UrlNormError
from ._parts import UrlParts

_SCHEME_FIRST = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
_SCHEME_REST = _SCHEME_FIRST | set("0123456789+-.")


def _split_scheme(url: str) -> tuple[str, str]:
    """Peel a valid RFC-3986 scheme off the front of *url*.

    Returns ``("", url)`` if no scheme is present.
    """
    if not url or url[0] not in _SCHEME_FIRST:
        return "", url
    end = 1
    while end < len(url) and url[end] in _SCHEME_REST:
        end += 1
    if end >= len(url) or url[end] != ":":
        return "", url
    return url[:end], url[end + 1 :]


def _split_fragment(url: str) -> tuple[str, str]:
    """Split off the fragment (the ``#...`` tail), if any."""
    idx = url.find("#")
    if idx < 0:
        return url, ""
    return url[:idx], url[idx + 1 :]


def _split_query(url: str) -> tuple[str, str]:
    """Split off the query (the ``?...`` tail), if any."""
    idx = url.find("?")
    if idx < 0:
        return url, ""
    return url[:idx], url[idx + 1 :]


def _split_authority(rest: str) -> tuple[bool, str, str]:
    """Detect a ``//authority`` prefix and return ``(present, authority, path)``."""
    if not rest.startswith("//"):
        return False, "", rest
    body = rest[2:]
    end = len(body)
    for ch in "/?#":
        idx = body.find(ch)
        if 0 <= idx < end:
            end = idx
    return True, body[:end], body[end:]


def _split_userinfo(authority: str) -> tuple[str, str]:
    """Pull userinfo off the front of an authority, if any."""
    at = authority.rfind("@")
    if at < 0:
        return "", authority
    return authority[:at], authority[at + 1 :]


def _split_host_port(hostport: str) -> tuple[str, int | None]:
    """Split ``host[:port]``, honoring ``[ipv6]`` brackets."""
    if hostport.startswith("["):
        close = hostport.find("]")
        if close < 0:
            raise UrlNormError("unterminated IPv6 host literal")
        host = hostport[: close + 1]
        tail = hostport[close + 1 :]
        if not tail:
            return host, None
        if not tail.startswith(":"):
            raise UrlNormError("garbage after IPv6 host literal")
        return host, _parse_port(tail[1:])
    colon = hostport.rfind(":")
    if colon < 0:
        return hostport, None
    return hostport[:colon], _parse_port(hostport[colon + 1 :])


def _parse_port(raw: str) -> int | None:
    """Validate a port string. Empty string means "absent"."""
    if raw == "":
        return None
    if not raw.isdigit():
        raise UrlNormError(f"invalid port: {raw!r}")
    value = int(raw)
    if value < 0 or value > 65535:
        raise UrlNormError(f"port out of range: {value}")
    return value


def parse(url: str) -> UrlParts:
    """Parse *url* into a :class:`UrlParts` value (no normalization)."""
    if not isinstance(url, str):
        raise UrlNormError(f"url must be str, got {type(url).__name__}")
    scheme, after_scheme = _split_scheme(url)
    body, fragment = _split_fragment(after_scheme)
    body, query = _split_query(body)
    has_authority, authority, path = _split_authority(body)
    userinfo, hostport = ("", "")
    port: int | None = None
    host = ""
    if has_authority:
        userinfo, hostport = _split_userinfo(authority)
        host, port = _split_host_port(hostport)
    return UrlParts(
        scheme=scheme,
        userinfo=userinfo,
        host=host,
        port=port,
        path=path,
        query=query,
        fragment=fragment,
        has_authority=has_authority,
    )


def unparse(parts: UrlParts) -> str:
    """Re-assemble a :class:`UrlParts` value into a URL string."""
    if not isinstance(parts, UrlParts):
        raise UrlNormError("parts must be a UrlParts instance")
    out: list[str] = []
    if parts.scheme:
        out.append(parts.scheme + ":")
    if parts.has_authority:
        out.append("//" + parts.authority)
    out.append(parts.path)
    if parts.query:
        out.append("?" + parts.query)
    if parts.fragment:
        out.append("#" + parts.fragment)
    return "".join(out)
