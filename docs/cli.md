# CLI Reference

55 subcommands via `imdb <command> [args]`.

## Titles

| Command | Arguments | Description |
|---|---|---|
| `get` | `ID` | Full title details |
| `get-titles` | `ID [ID...]` | Batch fetch titles |
| `search` | `QUERY [--first N]` | Search titles |
| `cast` | `ID` | Cast and crew |
| `seasons` | `ID` | Season list |
| `episodes` | `ID SEASON` | Episode list |
| `reviews` | `ID` | User reviews |
| `trailer` | `ID` | Trailer info |

## Title Content

| Command | Arguments | Description |
|---|---|---|
| `trivia` | `ID` | Trivia items |
| `quotes` | `ID` | Memorable quotes |
| `goofs` | `ID` | Mistakes |
| `locations` | `ID` | Filming locations |
| `plots` | `ID` | Plot summaries |
| `images` | `ID` | Image gallery |
| `soundtrack` | `ID` | Soundtrack tracks |
| `videos` | `ID` | Video gallery |

## Title Business & Ratings

| Command | Arguments | Description |
|---|---|---|
| `box-office` | `ID` | Budget and gross |
| `company-credits` | `ID` | Production companies |
| `tech-specs` | `ID` | Runtime, aspect ratio, etc. |
| `release-dates` | `ID` | Release dates by country |
| `parents-guide` | `ID` | Content advisory |
| `keywords` | `ID` | Plot keywords |
| `awards` | `ID` | Award nominations |
| `watch` | `ID` | Streaming options |
| `certificate` | `ID` | Age rating |
| `production-status` | `ID` | Production stage |
| `engagement` | `ID` | Watchlist/review counts |
| `rating-histogram` | `ID` | Rating distribution |
| `meta` | `ID` | Keywords, controversies |

## Connections & External

| Command | Arguments | Description |
|---|---|---|
| `connections` | `ID` | Sequels, prequels, references |
| `akas` | `ID` | Alternative titles |
| `external-links` | `ID` | External reviews |
| `crazy-credits` | `ID` | Alternate credits |
| `faqs` | `ID` | Frequently asked questions |
| `news` | `ID` | News articles |
| `recommendations` | `ID` | More like this |
| `interests` | `ID` | Interest categories |
| `related-lists` | `ID` | Related lists |

## Charts

| Command | Arguments | Description |
|---|---|---|
| `chart` | `TYPE [--first N]` | Generic chart (e.g. `TOP_RATED_MOVIES`) |
| `top-rated-movies` | `[--first N]` | Top 250 |
| `top-rated-tv` | `[--first N]` | Top rated TV |
| `most-popular-movies` | `[--first N]` | Most popular movies |
| `most-popular-tv` | `[--first N]` | Most popular TV |
| `lowest-rated-movies` | `[--first N]` | Bottom 100 |
| `trending` | `[--first N]` | Trending titles |
| `popular` | `[--first N]` | Popular titles |

## People

| Command | Arguments | Description |
|---|---|---|
| `person` | `ID` | Full person profile |
| `get-names` | `ID [ID...]` | Batch fetch people |
| `search-person` | `QUERY [--first N]` | Search people |
| `name-known-for` | `ID [--first N]` | Known-for titles |
| `name-filmography` | `ID [--first N]` | Filmography titles |
| `name-height` | `ID` | Physical height |
| `name-age` | `ID` | Current age |
| `name-birth` | `ID` | Birth details |
| `name-death` | `ID` | Death details |
| `name-spouses` | `ID` | Relationship history |
| `name-awards` | `ID` | Award nominations |
| `name-images` | `ID` | Image gallery |
| `name-credits` | `ID` | All credited works |
| `name-other-works` | `ID` | Other works |
| `name-trivia` | `ID` | Personal trivia |
| `name-quotes` | `ID` | Personal quotes |
| `name-trademarks` | `ID` | Characteristic trademarks |
