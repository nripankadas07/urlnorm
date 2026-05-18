"""The :class:`UrlParts` value type."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional


@dataclass(frozen=True)
class UrlParts:
    """Decomposed URL components.

    All string fields are stored exactly as they appear in the source URL
    (no decoding, no case folding). ``port`` is stored as ``None`` when
    absent or as an :class:`int` in the range 0-65535. A leading ``/``
    on ``path`` indicates an absolute reference.
    """

    scheme: str = ""
    userinfo: str = ""
    host: str = ""
    port: Optional[int] = None
    path: str = ""
    query: str = ""
    fragment: str = ""
    has_authority: bool = False

    def replace(self, **changes: object) -> "UrlParts":
        """Return a copy with the named fields replaced."""
        return replace(self, **changes)  # type: ignore[arg-type]

    @property
    def authority(self) -> str:
        """Reconstruct the ``userinfo@host:port`` block (sans leading ``//``)."""
        if not self.has_authority:
            return ""
        out: list[str] = []
        if self.userinfo:
            out.append(self.userinfo + "@")
        out.append(self.host)
        if self.port is not None:
            out.append(":" + str(self.port))
        return "".join(out)


__all__ = ["UrlParts"]
