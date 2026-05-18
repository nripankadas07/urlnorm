"""Tests for query-string canonicalization."""

from __future__ import annotations

from urlnorm._query import canonicalize_query, split_pairs


def test_split_pairs_empty_query_returns_empty_list() -> None:
    assert split_pairs("") == []


def test_split_pairs_keeps_bare_keys() -> None:
    assert split_pairs("debug&trace=on") == [("debug", None), ("trace", "on")]


def test_split_pairs_drops_blank_pairs() -> None:
    assert split_pairs("a=1&&b=2") == [("a", "1"), ("b", "2")]


def test_split_pairs_keeps_empty_value() -> None:
    assert split_pairs("a=") == [("a", "")]


def test_canonicalize_query_uppercases_pct() -> None:
    assert canonicalize_query("a=%2f%41", sort=False) == "a=%2FA"


def test_canonicalize_query_sort_orders_keys_alphabetically() -> None:
    assert canonicalize_query("z=3&a=1&m=2", sort=True) == "a=1&m=2&z=3"


def test_canonicalize_query_no_sort_preserves_order() -> None:
    assert canonicalize_query("z=3&a=1&m=2", sort=False) == "z=3&a=1&m=2"


def test_canonicalize_query_bare_key_sorts_before_valued_key() -> None:
    out = canonicalize_query("a=1&a", sort=True)
    assert out == "a&a=1"


def test_canonicalize_query_stable_for_equal_keys() -> None:
    out = canonicalize_query("k=b&k=a&k=c", sort=True)
    assert out == "k=a&k=b&k=c"


def test_canonicalize_query_handles_only_separator() -> None:
    assert canonicalize_query("&&", sort=False) == ""
