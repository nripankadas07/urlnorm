"""Tests for the RFC-3986 §5.2.4 dot-segment-removal algorithm."""

from __future__ import annotations

import pytest

from urlnorm._path import remove_dot_segments


@pytest.mark.parametrize(
    ("inp", "expected"),
    [
        ("", ""),
        ("/", "/"),
        ("/a/b/c", "/a/b/c"),
        ("/a/b/./c", "/a/b/c"),
        ("/a/b/../c", "/a/c"),
        ("/a/b/c/./..", "/a/b/"),
        ("/a/b/c/./../..", "/a/"),
        ("/a/../../b", "/b"),
        ("/./a", "/a"),
        ("/../a", "/a"),
        ("a/b/c", "a/b/c"),
        ("a/./b", "a/b"),
        # Strict RFC 3986 §5.2.4 behavior: a/../b traverses "above" the
        # implied root and the rebuilt path keeps the algorithm-emitted
        # leading slash.
        ("a/../b", "/b"),
        ("./a", "a"),
        ("../a", "a"),
        (".", ""),
        ("..", ""),
        ("/.", "/"),
        ("/..", "/"),
        # The classic RFC 3986 example.
        ("/a/b/c/./../../g", "/a/g"),
        ("mid/content=5/../6", "mid/6"),
    ],
)
def test_remove_dot_segments_matches_rfc_examples(inp: str, expected: str) -> None:
    assert remove_dot_segments(inp) == expected


def test_remove_dot_segments_trailing_slash_preserved() -> None:
    assert remove_dot_segments("/a/b/") == "/a/b/"


def test_remove_dot_segments_handles_double_slash() -> None:
    # The algorithm doesn't collapse ``//``; it just walks segments.
    assert remove_dot_segments("/a//b") == "/a//b"


def test_remove_dot_segments_returns_empty_for_root_dotdot() -> None:
    # ``/..`` ends up with an empty input but the output buffer keeps ``/``.
    assert remove_dot_segments("/../") == "/"
