# IMDb Unofficial API

[![CI](https://github.com/yourusername/Imdb-unofficial-api/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/Imdb-unofficial-api/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/imdb-unofficial-api)](https://pypi.org/project/imdb-unofficial-api/)
[![Python versions](https://img.shields.io/pypi/pyversions/imdb-unofficial-api)](https://pypi.org/project/imdb-unofficial-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Unofficial Python SDK for IMDb's internal GraphQL API. Provides a clean, typed interface to access virtually all public IMDb data — titles, names, credits, ratings, reviews, media, box office, charts, and more.

No official API key required. Works by reverse-engineering the same endpoints the IMDb website uses.

---

## Features

- **56 endpoint methods** covering every major IMDb data category
- **Full type hints** — all responses are typed dataclasses
- **Sync + Async** — both `ImdbClient` and `AsyncImdbClient` with identical interfaces
- **CLI** — 55 subcommands via `imdb` command-line tool
- **Resilient** — built-in retry with exponential backoff for rate limits and transient errors
- **Optional caching** — in-memory TTL cache via `cache_ttl` parameter
- **Custom exceptions** — `ImdbError`, `ImdbNotFoundError`, `ImdbRateLimitError`, `ImdbGraphQLError`
- **Batch fetching** — fetch multiple titles or names in a single GraphQL roundtrip
- **Cursor pagination** — `search_page()`, `search_advanced_page()`, `search_person_page()` return next-page cursors
- **No external API key required** — uses the same public API as imdb.com

---

## Installation

```bash
pip install imdb-unofficial-api
```

Or from source:

```bash
git clone https://github.com/yourusername/Imdb-unofficial-api.git
cd Imdb-unofficial-api
pip install -e .
```

---

## Quick Start

### Sync client

```python
from imdb_unofficial_api import ImdbClient

with ImdbClient() as client:
    # Get a title
    title = client.get_title("tt1375666")
    print(f"{title.title} ({title.release_year}) — {title.rating.aggregate_rating}")

    # Search
    results = client.search("Inception")
    for r in results:
        print(f"  {r.id}  {r.title} ({r.year})")

    # Get a person
    person = client.get_name("nm0000138")
    print(f"{person.name}: born {person.birth_date}")

    # Charts
    top = client.get_top_rated_movies(first=10)
    for t in top:
        print(f"  {t.title} ({t.release_year}) — {t.rating.aggregate_rating}")
```

### Async client

```python
import asyncio
from imdb_unofficial_api import AsyncImdbClient

async def main():
    async with AsyncImdbClient() as client:
        title = await client.get_title("tt1375666")
        print(title.title)
        results = await client.search("Inception")
        for r in results:
            print(f"  {r.id}  {r.title}")

asyncio.run(main())
```

### CLI

```bash
# Get a title
imdb get tt1375666

# Search
imdb search "Inception"

# Top 250 movies
imdb top-rated-movies --first 10

# Person details
imdb person nm0000138

# Batch fetch
imdb get-titles tt1375666 tt0816692 tt0137523
```

---

## Endpoints Reference

### Titles

| Method | CLI | Description |
|---|---|---|
| `get_title(id)` | `get ID` | Full title details (genres, runtime, taglines, recommendations, series info) |
| `get_titles(*ids)` | `get-titles ID...` | Batch fetch multiple titles in one roundtrip |
| `search(query, first)` | `search QUERY` | Search titles by name |
| `search_page(query, first, after)` | — | Search with pagination cursor |
| `search_advanced(...)` | — | Advanced search with genre, rating, date, runtime filters |
| `search_advanced_page(...)` | — | Advanced search with pagination |
| `get_title_cast(id, category)` | `cast ID` | Cast and crew (optional category filter) |
| `get_title_seasons(id)` | `seasons ID` | Season list for series |
| `get_title_episodes(id, season)` | `episodes ID SEASON` | Episode list for a season |
| `get_title_reviews(id)` | `reviews ID` | User reviews |
| `get_title_metacritic(id)` | — | Metacritic critic reviews |
| `get_title_trailer(id)` | `trailer ID` | Trailer metadata and playback URLs |

### Title Content

| Method | CLI | Description |
|---|---|---|
| `get_title_trivia(id)` | `trivia ID` | Trivia items |
| `get_title_quotes(id)` | `quotes ID` | Memorable quotes |
| `get_title_goofs(id)` | `goofs ID` | Mistakes and errors |
| `get_title_locations(id)` | `locations ID` | Filming locations |
| `get_title_plot_summaries(id)` | `plots ID` | Plot summaries |
| `get_title_images(id)` | `images ID` | Title images/gallery |
| `get_title_soundtrack(id)` | `soundtrack ID` | Soundtrack tracks |
| `get_title_videos(id)` | `videos ID` | Video gallery |

### Title Business & Ratings

| Method | CLI | Description |
|---|---|---|
| `get_title_box_office(id)` | `box-office ID` | Budget, opening weekend, gross worldwide |
| `get_title_company_credits(id)` | `company-credits ID` | Production companies |
| `get_title_tech_specs(id)` | `tech-specs ID` | Runtime, aspect ratio, color, sound mix |
| `get_title_release_dates(id)` | `release-dates ID` | Release dates by country |
| `get_title_parents_guide(id)` | `parents-guide ID` | Parents guide / content advisory |
| `get_title_keywords(id)` | `keywords ID` | Plot keywords |
| `get_title_awards(id)` | `awards ID` | Award nominations and wins |
| `get_title_watch_options(id)` | `watch ID` | Streaming/rental/buy options |
| `get_title_certificate(id)` | `certificate ID` | Age rating certificate |
| `get_title_production_status(id)` | `production-status ID` | Production stage (announced, released, etc.) |
| `get_title_engagement(id)` | `engagement ID` | Watchlist, rating, and review counts |
| `get_title_rating_histogram(id)` | `rating-histogram ID` | Rating distribution breakdown |
| `get_title_meta(id)` | `meta ID` | Can't be unfriended, keywords, controversies |

### Connections & External

| Method | CLI | Description |
|---|---|---|
| `get_title_connections(id)` | `connections ID` | Prequels, sequels, spin-offs, references |
| `get_title_akas(id)` | `akas ID` | Alternative titles by country |
| `get_title_external_links(id)` | `external-links ID` | External reviews and articles |
| `get_title_crazy_credits(id)` | `crazy-credits ID` | Crazy/alternate credits |
| `get_title_faqs(id)` | `faqs ID` | Frequently asked questions |
| `get_title_news(id)` | `news ID` | News articles |
| `get_title_recommendations(id)` | `recommendations ID` | More like this |
| `get_title_interests(id)` | `interests ID` | User interest categories |
| `get_title_related_lists(id)` | `related-lists ID` | Related user-created lists |

### Charts

| Method | CLI | Description |
|---|---|---|
| `get_chart(type, first)` | `chart TYPE` | Generic chart by type |
| `get_top_rated_movies(first)` | `top-rated-movies` | IMDb Top 250 |
| `get_top_rated_tv(first)` | `top-rated-tv` | Top rated TV shows |
| `get_most_popular_movies(first)` | `most-popular-movies` | Most popular movies |
| `get_most_popular_tv(first)` | `most-popular-tv` | Most popular TV shows |
| `get_lowest_rated_movies(first)` | `lowest-rated-movies` | Bottom 100 |
| `get_trending(limit)` | `trending` | Trending titles |
| `get_popular(limit)` | `popular` | Popular titles |

### Names / People

| Method | CLI | Description |
|---|---|---|
| `get_name(id)` | `person ID` | Full person profile (bio, birth, death, filmography) |
| `get_names(*ids)` | `get-names ID...` | Batch fetch multiple people |
| `search_person(query, first)` | `search-person QUERY` | Search people by name |
| `search_person_page(query, first, after)` | — | Person search with pagination |
| `get_name_known_for(id, first)` | `name-known-for ID` | Curated known-for titles |
| `get_name_filmography_titles(id, first)` | `name-filmography ID` | Filmography as title objects |
| `get_name_height(id)` | `name-height ID` | Physical height |
| `get_name_age(id)` | `name-age ID` | Current age |
| `get_name_birth_details(id)` | `name-birth ID` | Birth date and place |
| `get_name_death_details(id)` | `name-death ID` | Death date, cause, place |
| `get_name_spouses(id)` | `name-spouses ID` | Spouse/relationship history |
| `get_name_awards(id)` | `name-awards ID` | Award nominations and wins |
| `get_name_images(id)` | `name-images ID` | Person image gallery |
| `get_name_credits(id)` | `name-credits ID` | All credited works |
| `get_name_other_works(id)` | `name-other-works ID` | Other works and endorsements |
| `get_name_trivia(id)` | `name-trivia ID` | Personal trivia |
| `get_name_quotes(id)` | `name-quotes ID` | Personal quotes |
| `get_name_trademarks(id)` | `name-trademarks ID` | Characteristic trademarks |

---

## Configuration

```python
from imdb_unofficial_api import ImdbClient

# With caching (60-second TTL)
client = ImdbClient(cache_ttl=60)

# Custom region and language
client = ImdbClient(country="GB", language="en-GB")

# Increase retries
client = ImdbClient(max_retries=5)
```

Available parameters:
- `country` — ISO country code for region-specific data (default: `US`)
- `language` — Language header (default: `en-US`)
- `timeout` — HTTP request timeout in seconds (default: `30.0`)
- `max_retries` — Number of retry attempts for transient errors (default: `3`)
- `cache_ttl` — In-memory cache TTL in seconds, 0 to disable (default: `0`)

---

## Exception Handling

```python
from imdb_unofficial_api import ImdbClient, ImdbNotFoundError, ImdbRateLimitError, ImdbGraphQLError

with ImdbClient() as client:
    try:
        title = client.get_title("tt0000000")
    except ImdbNotFoundError:
        print("Title not found")
    except ImdbRateLimitError:
        print("Rate limited — slow down!")
    except ImdbGraphQLError as e:
        print(f"API error: {e}")
```

---

## Pagination

```python
results, cursor = client.search_page("Inception", first=10)
while cursor:
    print(f"Page with {len(results)} results, next cursor: {cursor}")
    results, cursor = client.search_page("Inception", first=10, after=cursor)
```

Available on: `search_page`, `search_advanced_page`, `search_person_page`

---

## Development

```bash
# Install dev dependencies
pip install ruff mypy

# Lint
ruff check imdb_unofficial_api/

# Type check
mypy imdb_unofficial_api/ --ignore-missing-imports

# Run import test
python -c "from imdb_unofficial_api import ImdbClient, AsyncImdbClient; print('OK')"
```

---

## Architecture

The library works by reverse-engineering the private GraphQL API endpoint (`api.graphql.imdb.com`) that powers the IMDb website. All requests use standard HTTP headers to mimic a browser session — no authentication or API keys needed.

Key design decisions:
- **One class per client style** — `ImdbClient` (sync) and `AsyncImdbClient` (async) are independent, not wrappers
- **Typed dataclasses** — every response is parsed into a typed model for IDE autocompletion
- **No public dependencies beyond `httpx`** — lightweight and auditable
- **GraphQL aliasing** for batch operations — single roundtrip for multiple IDs

---

## Limitations

- This is an **unofficial** API — there is no SLA, and IMDb may change their internal API at any time
- Some fields may be `None` if the data is not available for a given title/person
- Rate limiting is handled with retries, but aggressive usage may trigger temporary blocks
- The library does not handle authentication-protected features (e.g., user watchlists, ratings)

---

## License

MIT License — see [LICENSE](LICENSE) for details.
