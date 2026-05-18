# urlnorm

Zero-dependency URL normalizer for Python. Lower-cases scheme and host,
strips default ports, canonicalizes percent-encoding, resolves dot
segments per RFC 3986 §5.2.4, and optionally sorts the query string —
so that two URLs that mean the same thing compare equal.

## Features

- Lower-cases scheme and host (preserves path/query case)
- Strips default ports for `http`, `https`, `ws`, `wss`, `ftp`,
  `gopher`, `nntp`, `ldap`, `ldaps`, `telnet`
- Canonical percent-encoding: hex digits upper-cased, encoded
  *unreserved* characters decoded (RFC 3986 §6.2.2.2)
- Dot-segment removal (`/a/./b/../c` → `/a/c`) per RFC 3986 §5.2.4
- Optional stable query-string sort
- Optional fragment stripping
- IPv6 host literals (`[::1]`, `[2001:db8::1]`) handled correctly
- Userinfo and fragment also percent-canonicalized
- Frozen `UrlParts` dataclass for direct component access
- Zero dependencies, fully type-annotated, ships `py.typed`
- 100% line + branch coverage, `mypy --strict` clean

## Install

```bash
pip install urlnorm
```

## Usage

```python
import urlnorm

urlnorm.normalize("HTTP://Example.com:80/a/./b/../c?b=2&a=1#frag")
# 'http://example.com/a/c?b=2&a=1#frag'

urlnorm.normalize("https://example.com/?z=3&a=1", sort_query=True)
# 'https://example.com/?a=1&z=3'

urlnorm.equivalent(
    "https://example.com/p%2fq",
    "https://example.com/p%2Fq",
)
# True

# Parse / unparse round-trip
parts = urlnorm.parse("https://user@host.example:8443/a/b?x=1#f")
parts.scheme   # 'https'
parts.userinfo # 'user'
parts.host     # 'host.example'
parts.port     # 8443
urlnorm.unparse(parts)
# 'https://user@host.example:8443/a/b?x=1#f'
```

## API

### `normalize(url, *, strip_default_port=True, strip_fragment=False, sort_query=False, remove_dots=True, default_scheme=None)`

Return the canonical string form of `url`.

| Argument             | Default | Effect                                              |
| -------------------- | :-----: | --------------------------------------------------- |
| `strip_default_port` | `True`  | Drop the port if it matches the scheme's default    |
| `strip_fragment`     | `False` | Discard the `#...` tail                             |
| `sort_query`         | `False` | Stable-sort query pairs by key                      |
| `remove_dots`        | `True`  | Apply RFC-3986 §5.2.4 dot-segment removal           |
| `default_scheme`     | `None`  | Attach this scheme when the input has none          |

Raises `UrlNormError` on non-string input, malformed authority, invalid
port, or an invalid `default_scheme`.

### `equivalent(a, b, **opts) -> bool`

Return `True` if `a` and `b` normalize to the same string. `opts` are
forwarded to `normalize`.

### `parse(url) -> UrlParts`

Split a URL into its components without normalizing.

### `unparse(parts) -> str`

Re-assemble a `UrlParts` value into a URL string.

### `UrlParts`

Frozen dataclass with `scheme`, `userinfo`, `host`, `port`, `path`,
`query`, `fragment`, `has_authority`, plus an `authority` property and
a `replace(**changes)` helper.

### `UrlNormError`

Subclass of `ValueError` raised for invalid inputs.

### `DEFAULT_PORTS`

Mapping of scheme → default port, exposed for inspection and extension.

## Non-goals

- IDNA / punycode conversion (kept zero-dep)
- DNS resolution or HTTP fetching
- Validation of non-hierarchical schemes (`mailto:`, `tel:`, etc.) beyond
  pass-through

## Running tests

```bash
pip install pytest pytest-cov
PYTHONPATH=src python3 -m pytest tests/ --cov=src/urlnorm --cov-branch
```

## License

MIT — see [LICENSE](LICENSE).
