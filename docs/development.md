# Development

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

| Parameter | Default | Description |
|---|---|---|
| `country` | `"US"` | ISO country code for region-specific data |
| `language` | `"en-US"` | Language header |
| `timeout` | `30.0` | HTTP request timeout in seconds |
| `max_retries` | `3` | Retry attempts for transient GraphQL errors |
| `cache_ttl` | `0` | In-memory cache TTL in seconds (`0` = disabled) |

---

## Exception Handling

| Exception | Raised When |
|---|---|
| `ImdbError` | Base exception for all API errors |
| `ImdbNotFoundError` | 404 — resource not found |
| `ImdbRateLimitError` | 429 — rate limited |
| `ImdbGraphQLError` | GraphQL API returns errors |

```python
from imdb_unofficial_api import ImdbClient, ImdbNotFoundError, ImdbRateLimitError

with ImdbClient() as c:
    try:
        t = c.get_title("tt0000000")
    except ImdbNotFoundError:
        print("Not found")
    except ImdbRateLimitError:
        print("Slow down!")
```

---

## Pagination

Search methods return `(results, next_cursor)`. Pass the cursor to get the next page:

```python
results, cursor = c.search_page("Inception", first=10)
while cursor:
    print(f"{len(results)} results, next: {cursor}")
    results, cursor = c.search_page("Inception", first=10, after=cursor)
```

Available on:
- `search_page()`
- `search_advanced_page()`
- `search_person_page()`

---

## Architecture

The library reverse-engineers the private GraphQL API at `api.graphql.imdb.com` — the same endpoint the IMDb website uses. All requests use standard browser-like HTTP headers. No authentication or API keys.

### Key design decisions

- **`ImdbClient`** (sync) and **`AsyncImdbClient`** (async) are independent implementations, not wrappers
- Every response is parsed into a typed dataclass for IDE autocompletion
- Only dependency is `httpx`
- Batch operations (`get_titles`, `get_names`) use GraphQL aliasing for a single roundtrip
- Retry logic with exponential backoff for transient errors (`INTERNAL_ERROR`, `TIMEOUT`)
- Optional in-memory caching via `cache_ttl`

### Models

All response models are dataclasses in `imdb_unofficial_api/models.py`:

| Model | Fields |
|---|---|
| `Title` | id, title, original_title, title_type, release_year, end_year, rating, poster_url, plot_outline, runtime_minutes, genres, countries, languages, taglines, recommendations, series_info, credits, certificates, production_status |
| `Name` | id, name, birth_date, death_date, bio, image_url, filmography |
| `SearchResult` | id, title, original_title, title_type, year, image_url, rating |
| `Rating` | aggregate_rating, vote_count, top_rank |
| `Credit` | name, id, image_url, category, characters, episodes |
| `Season` | season_number, title_count, episode_count |
| `EpisodeInfo` | id, title, season_number, episode_number, release_date, rating, image_url, plot |
| `UserReview` | id, author, author_rating, summary, text, spoiler, votes |
| 25+ more | See `models.py` for the full set |

### Limitations

- Unofficial — no SLA, IMDb may change their API at any time
- Some fields return `None` when data is unavailable
- Aggressive usage may trigger rate limiting
- Does not handle auth-protected features (user watchlists, ratings)
