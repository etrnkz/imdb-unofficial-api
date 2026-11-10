# IMDb Unofficial API

[![CI](https://github.com/etrnkz/imdb-unofficial-api/actions/workflows/ci.yml/badge.svg)](https://github.com/etrnkz/imdb-unofficial-api/actions/workflows/ci.yml)
[![Python versions](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13%20|%203.14-blue)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Unofficial Python SDK for IMDb's internal GraphQL API. **56 typed endpoints** covering titles, names, credits, charts, reviews, media, and more. No API key required.

---

## Install

```bash
pip install imdb-unofficial-api
```

## Quick Start

```python
from imdb_unofficial_api import ImdbClient

with ImdbClient() as c:
    t = c.get_title("tt1375666")
    print(f"{t.title} ({t.release_year}) — {t.rating.aggregate_rating}")
```

Async:

```python
import asyncio
from imdb_unofficial_api import AsyncImdbClient

async def main():
    async with AsyncImdbClient() as c:
        t = await c.get_title("tt1375666")
        print(t.title)

asyncio.run(main())
```

CLI:

```bash
imdb get tt1375666
imdb search "Inception" --first 10
imdb top-rated-movies --first 10
imdb person nm0000138
```

---

## Documentation

| File | Content |
|---|---|
| [`docs/endpoints.md`](docs/endpoints.md) | All 56 endpoint methods with descriptions, signatures, return types |
| [`docs/cli.md`](docs/cli.md) | All 55 CLI subcommands and flags |
| [`docs/development.md`](docs/development.md) | Configuration, exception handling, pagination, architecture |

---

## License

MIT
