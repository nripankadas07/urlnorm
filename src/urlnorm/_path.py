"""Dot-segment removal — RFC 3986 §5.2.4."""

from __future__ import annotations


def remove_dot_segments(path: str) -> str:
    """Apply the *Remove Dot Segments* algorithm to a URI path.

    Implementation follows the reference algorithm in RFC 3986 §5.2.4
    using an input buffer and an output buffer. Leading and trailing
    slashes are preserved according to the spec.
    """
    if path in ("", "/"):
        return path
    inp = path
    out = ""
    while inp:
        inp, out, handled = _consume_prefix(inp, out)
        if handled:
            continue
        seg_end = _next_segment_end(inp)
        out += inp[:seg_end]
        inp = inp[seg_end:]
    return out


def _consume_prefix(inp: str, out: str) -> tuple[str, str, bool]:
    """Consume a dot-segment prefix, returning ``(new_inp, new_out, handled)``."""
    if inp.startswith("../"):
        return inp[3:], out, True
    if inp.startswith("./"):
        return inp[2:], out, True
    if inp.startswith("/./"):
        return "/" + inp[3:], out, True
    if inp == "/.":
        return "/", out, True
    if inp.startswith("/../"):
        return "/" + inp[4:], _strip_last_segment(out), True
    if inp == "/..":
        return "/", _strip_last_segment(out), True
    if inp in (".", ".."):
        return "", out, True
    return inp, out, False


def _strip_last_segment(buf: str) -> str:
    """Remove the final ``/segment`` from *buf*."""
    slash = buf.rfind("/")
    return buf[:slash] if slash >= 0 else ""


def _next_segment_end(inp: str) -> int:
    """Index of the next ``/`` after position 0, or ``len(inp)``."""
    if inp.startswith("/"):
        idx = inp.find("/", 1)
    else:
        idx = inp.find("/")
    return len(inp) if idx < 0 else idx
