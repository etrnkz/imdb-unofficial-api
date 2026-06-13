# Endpoints Reference

All 56 methods are available on both `ImdbClient` (sync) and `AsyncImdbClient` (async) with identical signatures.

---

## Titles

| Method | Return | Description |
|---|---|---|
| `get_title(id)` | `Optional[Title]` | Full details: genres, runtime, taglines, recommendations, series info |
| `get_titles(*ids)` | `list[Title]` | Batch fetch multiple titles in one GraphQL roundtrip |
| `search(query, first=20)` | `list[SearchResult]` | Search titles by name |
| `search_page(query, first=20, after=None)` | `tuple[list[SearchResult], str\|None]` | Search with cursor pagination |
| `search_advanced(query, first=20, ...)` | `list[SearchResult]` | Advanced search with genre, rating, date, runtime filters |
| `search_advanced_page(...)` | `tuple[list[SearchResult], str\|None]` | Advanced search with pagination |
| `get_title_cast(id, category=None)` | `list[Credit]` | Cast and crew, optional category filter |
| `get_title_seasons(id)` | `list[Season]` | Season list for series |
| `get_title_episodes(id, season)` | `list[EpisodeInfo]` | Episodes for a season |
| `get_title_reviews(id)` | `list[UserReview]` | User reviews |
| `get_title_metacritic(id)` | `list[MetacriticReview]` | Metacritic critic reviews |
| `get_title_trailer(id)` | `Optional[Trailer]` | Trailer metadata and playback URLs |

---

## Title Content

| Method | Return | Description |
|---|---|---|
| `get_title_trivia(id)` | `list[TriviaItem]` | Trivia items |
| `get_title_quotes(id)` | `list[QuoteItem]` | Memorable quotes |
| `get_title_goofs(id)` | `list[GoofItem]` | Mistakes and errors |
| `get_title_locations(id)` | `list[str]` | Filming locations |
| `get_title_plot_summaries(id)` | `list[PlotSummary]` | Plot summaries |
| `get_title_images(id)` | `list[TitleImage]` | Image gallery |
| `get_title_soundtrack(id)` | `list[SoundtrackTrack]` | Soundtrack tracks |
| `get_title_videos(id)` | `list[TitleVideo]` | Video gallery |

---

## Title Business & Ratings

| Method | Return | Description |
|---|---|---|
| `get_title_box_office(id)` | `Optional[BoxOffice]` | Budget, opening weekend, gross worldwide |
| `get_title_company_credits(id)` | `list[CompanyCreditItem]` | Production companies |
| `get_title_tech_specs(id)` | `Optional[TechSpec]` | Runtime, aspect ratio, color, sound mix |
| `get_title_release_dates(id)` | `list[ReleaseDateItem]` | Release dates by country |
| `get_title_parents_guide(id)` | `list[ParentsGuideItem]` | Content advisory |
| `get_title_keywords(id)` | `list[KeywordItem]` | Plot keywords |
| `get_title_awards(id)` | `list[AwardNomination]` | Award nominations and wins |
| `get_title_watch_options(id)` | `list[WatchOptionItem]` | Streaming/rental/buy options |
| `get_title_certificate(id)` | `Optional[CertificateInfo]` | Age rating certificate |
| `get_title_production_status(id)` | `Optional[ProductionStatusInfo]` | Production stage |
| `get_title_engagement(id)` | `Optional[EngagementStats]` | Watchlist, rating, review counts |
| `get_title_rating_histogram(id)` | `list[RatingHistogramEntry]` | Rating distribution breakdown |
| `get_title_meta(id)` | `Optional[TitleMeta]` | Keywords, controversies, "can't be unfriended" |

---

## Connections & External

| Method | Return | Description |
|---|---|---|
| `get_title_connections(id)` | `list[TitleConnection]` | Prequels, sequels, spin-offs, references |
| `get_title_akas(id)` | `list[TitleAka]` | Alternative titles by country |
| `get_title_external_links(id)` | `list[ExternalLink]` | External reviews and articles |
| `get_title_crazy_credits(id)` | `list[CrazyCredit]` | Crazy/alternate credits |
| `get_title_faqs(id)` | `list[FaqItem]` | Frequently asked questions |
| `get_title_news(id)` | `list[NewsArticle]` | News articles |
| `get_title_recommendations(id)` | `list[Title]` | More like this |
| `get_title_interests(id)` | `list[InterestItem]` | User interest categories |
| `get_title_related_lists(id)` | `list[RelatedList]` | Related user-created lists |

---

## Charts

| Method | Return | Description |
|---|---|---|
| `get_chart(type, first=50)` | `list[Title]` | Generic chart by `ChartTitleType` enum |
| `get_top_rated_movies(first=50)` | `list[Title]` | IMDb Top 250 |
| `get_top_rated_tv(first=50)` | `list[Title]` | Top rated TV shows |
| `get_most_popular_movies(first=50)` | `list[Title]` | Most popular movies |
| `get_most_popular_tv(first=50)` | `list[Title]` | Most popular TV shows |
| `get_lowest_rated_movies(first=100)` | `list[Title]` | Bottom 100 |
| `get_trending(limit=50)` | `list[Title]` | Trending titles |
| `get_popular(limit=50)` | `list[Title]` | Popular titles |

---

## Names

| Method | Return | Description |
|---|---|---|
| `get_name(id)` | `Optional[Name]` | Full profile: bio, birth, death, filmography |
| `get_names(*ids)` | `list[Name]` | Batch fetch multiple people in one roundtrip |
| `search_person(query, first=20)` | `list[SearchResult]` | Search people by name |
| `search_person_page(query, first=20, after=None)` | `tuple[list[SearchResult], str\|None]` | Person search with pagination |
| `get_name_known_for(id, first=12)` | `list[Title]` | Curated known-for titles |
| `get_name_filmography_titles(id, first=25)` | `list[Title]` | Filmography as title objects |
| `get_name_height(id)` | `Optional[NameHeight]` | Physical height |
| `get_name_age(id)` | `Optional[NameAge]` | Current age |
| `get_name_birth_details(id)` | `Optional[NameBirthDetails]` | Birth date and place |
| `get_name_death_details(id)` | `Optional[NameDeathDetails]` | Death date, cause, place |
| `get_name_spouses(id)` | `list[NameSpouse]` | Spouse/relationship history |
| `get_name_awards(id)` | `list[NameAward]` | Award nominations and wins |
| `get_name_images(id)` | `list[TitleImage]` | Image gallery |
| `get_name_credits(id)` | `list[NameCredit]` | All credited works |
| `get_name_other_works(id)` | `list[NameOtherWork]` | Other works and endorsements |
| `get_name_trivia(id)` | `list[NameTriviaItem]` | Personal trivia |
| `get_name_quotes(id)` | `list[NameQuoteItem]` | Personal quotes |
| `get_name_trademarks(id)` | `list[NameTrademark]` | Characteristic trademarks |
