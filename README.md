# Imdb-unofficial-api

Unofficial Python API client for IMDb, powered by reverse-engineering the internal GraphQL API at `api.graphql.imdb.com`.

## Features

- **Title lookup** — get movies, TV shows, episodes with ratings, plot, cast, genres, recommendations, and more
- **Person lookup** — actors, directors, writers with bios, birth/death dates, known-for filmography
- **Search** — search titles by query string
- **Full credits** — get complete cast list with character names
- **Fast** — direct GraphQL queries, no HTML parsing, no browser required
- **No API key needed** — uses IMDb's own internal API

## Installation

```bash
pip install httpx
git clone https://github.com/yourusername/Imdb-unofficial-api
cd Imdb-unofficial-api
```

## Quick Start

```python
from imdb_unofficial_api import ImdbClient

client = ImdbClient()

# Get a movie
title = client.get_title("tt0111161")
print(title.title)           # "The Shawshank Redemption"
print(title.rating.aggregate_rating)  # 9.3
print(title.plot_outline)    # Plot summary
print(title.genres)          # ["Drama"]

# Get an actor
name = client.get_name("nm0000138")
print(name.name)             # "Leonardo DiCaprio"
print(name.birth_date)       # "1974-11-11"
for movie in name.filmography:
    print(f"  {movie.title} ({movie.release_year})")

# Search titles
results = client.search("Inception")
for r in results:
    print(f"[{r.id}] {r.title} ({r.year}) - {r.rating}")

# Get cast list
cast = client.get_title_cast("tt0111161")
for c in cast[:10]:
    print(f"{c.name} as {', '.join(c.characters)}")
```

## API Reference

### `ImdbClient(country="US", language="en-US", timeout=30)`

Create a new client. Optional country/language for localized results.

### `get_title(title_id) -> Title`

Look up a movie/TV show by its IMDb ID (e.g. `"tt0111161"` or `"0111161"`).

**Title fields:**
- `id`, `title`, `original_title`, `title_type`, `release_year`, `end_year`
- `rating` (Rating: `aggregate_rating`, `vote_count`, `top_rank`)
- `plot_outline`, `runtime_minutes`, `genres`, `countries`, `languages`
- `poster_url`, `popularity_rank`, `taglines`
- `directors`, `writers` (list of Credit)
- `recommendations` (list of Title)
- `raw` (raw API response dict)

### `search(query, first=20) -> list[SearchResult]`

Search for titles matching `query`.

**SearchResult fields:** `id`, `title`, `original_title`, `title_type`, `year`, `image_url`, `rating`

### `get_name(name_id) -> Name`

Look up a person by their IMDb ID (e.g. `"nm0000138"` or `"0000138"`).

**Name fields:** `id`, `name`, `birth_date`, `death_date`, `bio`, `image_url`, `filmography` (list of Title), `raw`

### `get_title_cast(title_id, category=None) -> list[Credit]`

Get the full cast list. Optionally filter by category (e.g. `"cast"`, `"director"`, `"writer"`).

**Credit fields:** `person_id`, `name`, `characters`, `category`, `attributes`, `image_url`

## How It Works

This library uses the same GraphQL API that powers the IMDb website:
- **Endpoint**: `https://api.graphql.imdb.com/`
- **Method**: POST with JSON body containing `operationName`, `query`, and `variables`
- **Auth**: None required — the API is publicly accessible (with usage limitations)

## Disclaimer

This project is not affiliated with, endorsed by, or connected to IMDb or Amazon. All data belongs to IMDb. This is for educational purposes only. Respect IMDb's terms of service and robots.txt.
