import httpx
import asyncio
import time
from typing import Optional, Any
from .exceptions import (
    ImdbError,
    ImdbNotFoundError,
    ImdbRateLimitError,
    ImdbGraphQLError,
)
from .exceptions import (
    ImdbError,
    ImdbNotFoundError,
    ImdbRateLimitError,
    ImdbGraphQLError,
)
from .models import (
    Title,
    Name,
    SearchResult,
    Rating,
    Credit,
    Season,
    EpisodeInfo,
    UserReview,
    MetacriticReview,
    Trailer,
    TriviaItem,
    QuoteItem,
    GoofItem,
    BoxOffice,
    CompanyCreditItem,
    TechSpec,
    ReleaseDateItem,
    ParentsGuideItem,
    KeywordItem,
    AwardNomination,
    WatchOptionItem,
    PlotSummary,
    TitleImage,
    SoundtrackTrack,
    TitleConnection,
    TitleAka,
    ExternalLink,
    CrazyCredit,
    FaqItem,
    NewsArticle,
    CertificateInfo,
    ProductionStatusInfo,
    EngagementStats,
    RatingHistogramEntry,
    TitleVideo,
    TitleMeta,
    InterestItem,
    RelatedList,
    NameHeight,
    NameAge,
    NameBirthDetails,
    NameDeathDetails,
    NameSpouse,
    NameAward,
    NameCredit,
    NameOtherWork,
    NameTriviaItem,
    NameQuoteItem,
    NameTrademark,
)

GRAPHQL_URL = "https://api.graphql.imdb.com/"

DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Origin": "https://www.imdb.com",
    "Referer": "https://www.imdb.com/",
}

from .client import (
    GET_TITLE_QUERY,
    SEARCH_QUERY,
    PERSON_SEARCH_QUERY,
    GET_NAME_QUERY,
    GET_NAME_KNOWN_FOR_QUERY,
    GET_TITLE_FULL_CREDITS_QUERY,
    GET_TITLE_CREDITS_BY_CATEGORY,
    GET_TITLE_SEASONS_QUERY,
    GET_TITLE_EPISODES_QUERY,
    GET_TITLE_REVIEWS_QUERY,
    GET_TITLE_MEDIA_QUERY,
    ADVANCED_SEARCH_QUERY_BASE,
    GET_TITLE_EXTRAS_QUERY,
    GET_TITLE_INFO_QUERY,
    GET_TITLE_DETAILS_QUERY,
    GET_TITLE_RECOMMENDATIONS_QUERY,
    GET_TITLE_META_QUERY,
    GET_NAME_DETAILS_QUERY,
)


class AsyncImdbClient:
    def __init__(
        self,
        country: Optional[str] = "US",
        language: Optional[str] = "en-US",
        timeout: float = 30.0,
        max_retries: int = 3,
        cache_ttl: int = 0,
    ):
        self._client = httpx.AsyncClient(
            headers=dict(DEFAULT_HEADERS),
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
        )
        if country:
            self._client.headers["X-Imdb-User-Country"] = country
        if language:
            self._client.headers["X-Imdb-User-Language"] = language
        self._max_retries = max_retries
        self._cache: dict[str, tuple[float, dict]] = {}
        self._cache_ttl = cache_ttl

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self._client.aclose()

    def _cache_key(self, query: str, variables: dict) -> str:
        return f"{query}|{variables}"

    async def _graphql(
        self,
        query: str,
        variables: dict[str, Any],
        operation_name: Optional[str] = None,
    ) -> dict:
        ck = self._cache_key(query, variables)
        if self._cache_ttl > 0 and ck in self._cache:
            ts, data = self._cache[ck]
            if time.time() - ts < self._cache_ttl:
                return data

        payload: dict[str, Any] = {"query": query, "variables": variables}
        if operation_name:
            payload["operationName"] = operation_name

        for attempt in range(self._max_retries):
            resp = await self._client.post(GRAPHQL_URL, json=payload)
            if resp.status_code == 429:
                raise ImdbRateLimitError("Rate limited by IMDb API")
            if resp.status_code == 404:
                raise ImdbNotFoundError("Resource not found")
            resp.raise_for_status()
            data = resp.json()

            if "errors" in data:
                is_retriable = any(
                    e.get("extensions", {}).get("code") in ("INTERNAL_ERROR", "TIMEOUT")
                    for e in data["errors"]
                )
                if is_retriable and attempt < self._max_retries - 1:
                    await asyncio.sleep(2**attempt)
                    continue
                raise ImdbGraphQLError(str(data["errors"]))

            result = data.get("data", {})
            if self._cache_ttl > 0:
                self._cache[ck] = (time.time(), result)
            return result

        raise ImdbError("Max retries exceeded")

    async def get_title(self, title_id: str) -> Optional[Title]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_QUERY, {"id": tid}, "GetTitle")
        title_data = data.get("title")
        if not title_data:
            return None
        from .client import ImdbClient

        return ImdbClient._parse_title(None, title_data)

    async def get_titles(self, *ids: str) -> list[Title]:
        parts: list[str] = []
        for i, tid in enumerate(ids):
            tid_norm = tid if tid.startswith("tt") else f"tt{tid}"
            parts.append(
                f't{i}: title(id: "{tid_norm}") {{ id titleText {{ text }} titleType {{ text }} '
                f"releaseYear {{ year }} ratingsSummary {{ aggregateRating }} primaryImage {{ url }} }}"
            )
        if not parts:
            return []
        q = "{{ {} }}".format(" ".join(parts))
        data = await self._graphql(q, {})
        results: list[Title] = []
        for i in range(len(ids)):
            node = data.get(f"t{i}")
            if not node:
                continue
            t = Title(id=node.get("id"), title=node.get("titleText", {}).get("text"))
            t.title_type = node.get("titleType", {}).get("text")
            t.release_year = node.get("releaseYear", {}).get("year")
            t.poster_url = node.get("primaryImage", {}).get("url")
            rs = node.get("ratingsSummary")
            if rs:
                t.rating = Rating(aggregate_rating=rs.get("aggregateRating") or 0.0)
            results.append(t)
        return results

    async def get_names(self, *ids: str) -> list[Name]:
        parts: list[str] = []
        for i, nid in enumerate(ids):
            nid_norm = nid if nid.startswith("nm") else f"nm{nid}"
            parts.append(
                f'n{i}: name(id: "{nid_norm}") {{ id nameText {{ text }} primaryImage {{ url }} }}'
            )
        if not parts:
            return []
        q = "{{ {} }}".format(" ".join(parts))
        data = await self._graphql(q, {})
        results: list[Name] = []
        for i in range(len(ids)):
            node = data.get(f"n{i}")
            if not node:
                continue
            n = Name(id=node.get("id"), name=node.get("nameText", {}).get("text"))
            n.image_url = node.get("primaryImage", {}).get("url")
            results.append(n)
        return results

    async def search(self, query: str, first: int = 20) -> list[SearchResult]:
        return (await self.search_page(query, first=first))[0]

    async def search_page(
        self, query: str, first: int = 20, after: Optional[str] = None
    ) -> tuple[list[SearchResult], Optional[str]]:
        data = await self._graphql(
            SEARCH_QUERY,
            {"searchTerm": query, "first": first, "after": after},
            "Search",
        )
        results: list[SearchResult] = []
        for edge in data.get("mainSearch", {}).get("edges", []):
            node = edge.get("node", {}).get("entity", {})
            if not node.get("id") or not node["id"].startswith("tt"):
                continue
            sr = SearchResult(
                id=node.get("id"),
                title=node.get("titleText", {}).get("text"),
                original_title=node.get("originalTitleText", {}).get("text"),
                title_type=node.get("titleType", {}).get("text"),
                year=(node.get("releaseYear") or {}).get("year"),
                image_url=(node.get("primaryImage") or {}).get("url"),
            )
            rs = node.get("ratingsSummary")
            if rs:
                sr.rating = rs.get("aggregateRating")
            results.append(sr)
        pi = data.get("mainSearch", {}).get("pageInfo", {})
        cursor = pi.get("endCursor") if pi.get("hasNextPage") else None
        return results, cursor

    async def search_person(self, query: str, first: int = 20) -> list[SearchResult]:
        return (await self.search_person_page(query, first=first))[0]

    async def search_person_page(
        self, query: str, first: int = 20, after: Optional[str] = None
    ) -> tuple[list[SearchResult], Optional[str]]:
        data = await self._graphql(
            PERSON_SEARCH_QUERY,
            {"searchTerm": query, "first": first, "after": after},
            "SearchPerson",
        )
        results: list[SearchResult] = []
        for edge in data.get("mainSearch", {}).get("edges", []):
            node = edge.get("node", {}).get("entity", {})
            if not node.get("id"):
                continue
            results.append(
                SearchResult(
                    id=node.get("id"),
                    title=node.get("nameText", {}).get("text"),
                    image_url=(node.get("primaryImage") or {}).get("url"),
                )
            )
        pi = data.get("mainSearch", {}).get("pageInfo", {})
        cursor = pi.get("endCursor") if pi.get("hasNextPage") else None
        return results, cursor

    async def search_advanced(
        self,
        query: Optional[str] = None,
        first: int = 20,
        title_type: Optional[str] = None,
        genre_ids: Optional[str] = None,
        min_rating: Optional[float] = None,
        release_date_start: Optional[str] = None,
        release_date_end: Optional[str] = None,
        min_runtime: Optional[int] = None,
        max_runtime: Optional[int] = None,
    ) -> list[SearchResult]:
        return (
            await self.search_advanced_page(
                query=query,
                first=first,
                title_type=title_type,
                genre_ids=genre_ids,
                min_rating=min_rating,
                release_date_start=release_date_start,
                release_date_end=release_date_end,
                min_runtime=min_runtime,
                max_runtime=max_runtime,
            )
        )[0]

    async def search_advanced_page(
        self,
        query: Optional[str] = None,
        first: int = 20,
        after: Optional[str] = None,
        title_type: Optional[str] = None,
        genre_ids: Optional[str] = None,
        min_rating: Optional[float] = None,
        release_date_start: Optional[str] = None,
        release_date_end: Optional[str] = None,
        min_runtime: Optional[int] = None,
        max_runtime: Optional[int] = None,
    ) -> tuple[list[SearchResult], Optional[str]]:
        constraints_parts: list[str] = []
        if query:
            constraints_parts.append(
                f'titleTextConstraint: {{searchTerm: "{query}", useFuzzySearch: true}}'
            )
        if title_type:
            constraints_parts.append(
                f'titleTypeConstraint: {{anyTitleTypeIds: "{title_type}"}}'
            )
        if genre_ids:
            constraints_parts.append(f'genreConstraint: {{anyGenreIds: "{genre_ids}"}}')
        if min_rating is not None:
            constraints_parts.append(
                f"userRatingsConstraint: {{aggregateRatingRange: {{min: {min_rating}}}}}"
            )
        if release_date_start or release_date_end:
            d = []
            if release_date_start:
                d.append(f'start: "{release_date_start}"')
            if release_date_end:
                d.append(f'end: "{release_date_end}"')
            constraints_parts.append(
                f"releaseDateConstraint: {{releaseDateRange: {{{','.join(d)}}}}}"
            )
        if min_runtime is not None or max_runtime is not None:
            d = []
            if min_runtime is not None:
                d.append(f"min: {min_runtime}")
            if max_runtime is not None:
                d.append(f"max: {max_runtime}")
            constraints_parts.append(
                f"runtimeConstraint: {{runtimeRangeMinutes: {{{','.join(d)}}}}}"
            )

        if constraints_parts:
            constraints_str = ", constraints:{" + ",".join(constraints_parts) + "}"
            query_str = ADVANCED_SEARCH_QUERY_BASE.replace(
                "{CONSTRAINTS}", constraints_str
            )
        else:
            query_str = ADVANCED_SEARCH_QUERY_BASE.replace("{CONSTRAINTS}", "")

        data = await self._graphql(
            query_str, {"first": first, "after": after}, "AdvancedSearch"
        )
        results: list[SearchResult] = []
        for edge in data.get("advancedTitleSearch", {}).get("edges", []):
            node = edge.get("node", {}).get("title", {})
            if not node.get("id"):
                continue
            sr = SearchResult(
                id=node.get("id"),
                title=node.get("titleText", {}).get("text"),
                original_title=node.get("originalTitleText", {}).get("text"),
                title_type=node.get("titleType", {}).get("text"),
                year=(node.get("releaseYear") or {}).get("year"),
                image_url=(node.get("primaryImage") or {}).get("url"),
            )
            rs = node.get("ratingsSummary")
            if rs:
                sr.rating = rs.get("aggregateRating")
            results.append(sr)
        pi = data.get("advancedTitleSearch", {}).get("pageInfo", {})
        cursor = pi.get("endCursor") if pi.get("hasNextPage") else None
        return results, cursor

    async def search_person(self, query: str, first: int = 20) -> list[SearchResult]:
        return (await self.search_person_page(query, first=first))[0]

    async def search_person_page(
        self, query: str, first: int = 20, after: Optional[str] = None
    ) -> tuple[list[SearchResult], Optional[str]]:
        data = await self._graphql(
            PERSON_SEARCH_QUERY,
            {"searchTerm": query, "first": first, "after": after},
            "SearchPerson",
        )
        results: list[SearchResult] = []
        for edge in data.get("mainSearch", {}).get("edges", []):
            node = edge.get("node", {}).get("entity", {})
            if not node.get("id"):
                continue
            results.append(
                SearchResult(
                    id=node.get("id"),
                    title=node.get("nameText", {}).get("text"),
                    image_url=(node.get("primaryImage") or {}).get("url"),
                )
            )
        pi = data.get("mainSearch", {}).get("pageInfo", {})
        cursor = pi.get("endCursor") if pi.get("hasNextPage") else None
        return results, cursor

    async def get_name(self, name_id: str) -> Optional[Name]:
        nid = name_id if name_id.startswith("nm") else f"nm{name_id}"
        data = await self._graphql(GET_NAME_QUERY, {"id": nid}, "GetName")
        name_data = data.get("name")
        if not name_data:
            return None
        from .client import ImdbClient

        return ImdbClient._parse_name(None, name_data)

    async def get_title_cast(
        self, title_id: str, category: Optional[str] = None
    ) -> list[Credit]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        if category:
            data = await self._graphql(
                GET_TITLE_CREDITS_BY_CATEGORY,
                {"id": tid, "category": category},
                "GetCreditsByCategory",
            )
        else:
            data = await self._graphql(
                GET_TITLE_FULL_CREDITS_QUERY,
                {"id": tid},
                "GetFullCredits",
            )
        credits: list[Credit] = []
        for edge in data.get("title", {}).get("credits", {}).get("edges", []):
            node = edge.get("node", {})
            name_node = node.get("name") or {}
            c = Credit(
                person_id=name_node.get("id"),
                name=name_node.get("nameText", {}).get("text"),
                image_url=(name_node.get("primaryImage") or {}).get("url"),
            )
            if node.get("characters"):
                c.characters = [
                    ch.get("name", "") for ch in node["characters"] if ch.get("name")
                ]
            if node.get("attributes"):
                c.attributes = [
                    attr.get("text", "")
                    for attr in node["attributes"]
                    if attr.get("text")
                ]
            credits.append(c)
        return credits

    async def get_title_seasons(self, title_id: str) -> list[Season]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_SEASONS_QUERY, {"id": tid}, "GetSeasons")
        seasons: list[Season] = []
        for edge in (
            data.get("title", {})
            .get("episodes", {})
            .get("displayableSeasons", {})
            .get("edges", [])
        ):
            node = edge.get("node", {})
            seasons.append(
                Season(season_number=node.get("season"), text=node.get("text"))
            )
        return seasons

    async def get_title_episodes(
        self, title_id: str, season: Optional[str] = None, first: int = 50
    ) -> list[Title]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        seasons_filter = [str(season)] if season is not None else ["1"]
        data = await self._graphql(
            GET_TITLE_EPISODES_QUERY,
            {"id": tid, "first": first, "seasons": seasons_filter},
            "GetEpisodes",
        )
        episodes: list[Title] = []
        for edge in (
            data.get("title", {})
            .get("episodes", {})
            .get("episodes", {})
            .get("edges", [])
        ):
            node = edge.get("node", {})
            t = Title(
                id=node.get("id"),
                title=node.get("titleText", {}).get("text"),
                release_year=(node.get("releaseYear") or {}).get("year"),
                poster_url=(node.get("primaryImage") or {}).get("url"),
            )
            if node.get("ratingsSummary"):
                t.rating = Rating(
                    aggregate_rating=node["ratingsSummary"].get("aggregateRating")
                    or 0.0,
                    vote_count=node["ratingsSummary"].get("voteCount") or 0,
                )
            if node.get("series") and node["series"].get("displayableEpisodeNumber"):
                den = node["series"]["displayableEpisodeNumber"]
                ei = EpisodeInfo()
                if den.get("displayableSeason"):
                    ei.season_number = den["displayableSeason"].get("season")
                if den.get("episodeNumber"):
                    ei.episode_number = den["episodeNumber"].get("episodeNumber")
                    ei.text = den["episodeNumber"].get("text")
                t.episode_info = ei
            episodes.append(t)
        return episodes

    async def get_title_reviews(
        self, title_id: str
    ) -> tuple[list[UserReview], list[MetacriticReview], Optional[int]]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_REVIEWS_QUERY, {"id": tid}, "GetReviews")
        title_data = data.get("title", {})
        metacritic_score: Optional[int] = None
        mc = title_data.get("metacritic", {})
        if mc.get("metascore"):
            metacritic_score = mc["metascore"].get("score")
        metacritic_reviews: list[MetacriticReview] = []
        for edge in mc.get("reviews", {}).get("edges", []):
            n = edge.get("node", {})
            metacritic_reviews.append(
                MetacriticReview(
                    score=n.get("score"),
                    reviewer=n.get("reviewer"),
                    quote=n.get("quote", {}).get("value"),
                    site=n.get("site"),
                    url=n.get("url"),
                )
            )
        user_reviews: list[UserReview] = []
        for edge in title_data.get("reviews", {}).get("edges", []):
            n = edge.get("node", {})
            h = n.get("helpfulness", {})
            user_reviews.append(
                UserReview(
                    id=n.get("id"),
                    author=n.get("author", {}).get("username", {}).get("text"),
                    author_rating=n.get("authorRating"),
                    summary=n.get("summary", {}).get("originalText"),
                    text=n.get("text", {}).get("originalText", {}).get("markdown"),
                    spoiler=n.get("spoiler", False),
                    up_votes=h.get("upVotes", 0),
                    down_votes=h.get("downVotes", 0),
                    helpfulness_score=h.get("score"),
                    submission_date=n.get("submissionDate"),
                )
            )
        return user_reviews, metacritic_reviews, metacritic_score

    async def get_chart(self, chart_type: str, first: int = 50) -> list[Title]:
        query_str = f"""
query GetChart($first: Int!) {{
  chartTitles(first: $first, chart: {{chartType: {chart_type}}}) {{
    edges {{
      node {{
        id
        titleText {{ text }}
        releaseYear {{ year }}
        ratingsSummary {{ aggregateRating voteCount topRanking {{ rank }} }}
        primaryImage {{ url }}
        titleType {{ text }}
      }}
    }}
  }}
}}
"""
        data = await self._graphql(query_str, {"first": first}, "GetChart")
        from .client import ImdbClient

        return [
            ImdbClient._parse_chart_title(None, edge.get("node", {}))
            for edge in data.get("chartTitles", {}).get("edges", [])
        ]

    async def get_trending(self, limit: int = 50) -> list[Title]:
        query_str = """
query GetTrending($limit: Int!) {
  trendingTitles(limit: $limit) {
    titles {
      id
      titleText { text }
      releaseYear { year }
      ratingsSummary { aggregateRating }
      primaryImage { url }
      titleType { text }
    }
  }
}
"""
        data = await self._graphql(query_str, {"limit": limit})
        from .client import ImdbClient

        return [
            ImdbClient._parse_chart_title(None, node)
            for node in data.get("trendingTitles", {}).get("titles", [])
        ]

    async def get_popular(self, limit: int = 50) -> list[Title]:
        query_str = """
query GetPopular($limit: Int!) {
  popularTitles(limit: $limit) {
    titles {
      id
      titleText { text }
      releaseYear { year }
      ratingsSummary { aggregateRating }
      primaryImage { url }
      titleType { text }
    }
  }
}
"""
        data = await self._graphql(query_str, {"limit": limit})
        from .client import ImdbClient

        return [
            ImdbClient._parse_chart_title(None, node)
            for node in data.get("popularTitles", {}).get("titles", [])
        ]

    async def get_top_rated_movies(self, first: int = 50) -> list[Title]:
        return await self.get_chart("TOP_RATED_MOVIES", first)

    async def get_top_rated_tv(self, first: int = 50) -> list[Title]:
        return await self.get_chart("TOP_RATED_TV_SHOWS", first)

    async def get_most_popular_movies(self, first: int = 50) -> list[Title]:
        return await self.get_chart("MOST_POPULAR_MOVIES", first)

    async def get_most_popular_tv(self, first: int = 50) -> list[Title]:
        return await self.get_chart("MOST_POPULAR_TV_SHOWS", first)

    async def get_lowest_rated_movies(self, first: int = 50) -> list[Title]:
        return await self.get_chart("LOWEST_RATED_MOVIES", first)

    async def get_title_trailer(self, title_id: str) -> Optional[Trailer]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_MEDIA_QUERY, {"id": tid}, "GetMedia")
        lt = data.get("title", {}).get("latestTrailer")
        if not lt:
            return None
        t = Trailer(
            id=lt.get("id"),
            name=lt.get("name", {}).get("value"),
            description=lt.get("description", {}).get("value"),
            content_type=lt.get("contentType", {}).get("id"),
            duration_seconds=lt.get("runtime", {}).get("value"),
            thumbnail_url=lt.get("thumbnail", {}).get("url"),
        )
        for u in lt.get("playbackURLs", []):
            dn = u.get("displayName", {}).get("value")
            url = u.get("url")
            if dn and url:
                t.playback_urls[dn] = url
        return t

    async def get_title_trivia(self, title_id: str) -> list[TriviaItem]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_MEDIA_QUERY, {"id": tid}, "GetMedia")
        items: list[TriviaItem] = []
        for edge in data.get("title", {}).get("trivia", {}).get("edges", []):
            body = (
                edge.get("node", {})
                .get("displayableArticle", {})
                .get("body", {})
                .get("markdown")
            )
            if body:
                items.append(TriviaItem(text=body))
        return items

    async def get_title_quotes(self, title_id: str) -> list[QuoteItem]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_MEDIA_QUERY, {"id": tid}, "GetMedia")
        items: list[QuoteItem] = []
        for edge in data.get("title", {}).get("quotes", {}).get("edges", []):
            body = (
                edge.get("node", {})
                .get("displayableArticle", {})
                .get("body", {})
                .get("markdown")
            )
            if body:
                items.append(QuoteItem(text=body))
        return items

    async def get_title_goofs(self, title_id: str) -> list[GoofItem]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_MEDIA_QUERY, {"id": tid}, "GetMedia")
        items: list[GoofItem] = []
        for edge in data.get("title", {}).get("goofs", {}).get("edges", []):
            n = edge.get("node", {})
            text = n.get("text", {}).get("markdown")
            cat = n.get("category", {}).get("text")
            if text:
                items.append(GoofItem(text=text, category=cat))
        return items

    async def get_title_filming_locations(self, title_id: str) -> list[dict]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_MEDIA_QUERY, {"id": tid}, "GetMedia")
        items: list[dict] = []
        for edge in data.get("title", {}).get("filmingLocations", {}).get("edges", []):
            n = edge.get("node", {})
            attrs = [
                a.get("text", "") for a in n.get("attributes", []) if a.get("text")
            ]
            items.append(
                {
                    "location": n.get("location"),
                    "text": n.get("text"),
                    "attributes": attrs,
                }
            )
        return items

    async def get_title_box_office(self, title_id: str) -> Optional[BoxOffice]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_EXTRAS_QUERY, {"id": tid}, "GetExtras")
        t = data.get("title", {})
        bo = BoxOffice()
        if t.get("productionBudget", {}).get("budget"):
            bo.budget = t["productionBudget"]["budget"].get("amount")
            bo.budget_currency = t["productionBudget"]["budget"].get("currency")
        if t.get("lifetimeGross", {}).get("total"):
            bo.lifetime_gross = t["lifetimeGross"]["total"].get("amount")
            bo.lifetime_currency = t["lifetimeGross"]["total"].get("currency")
        if t.get("openingWeekendGross", {}).get("gross", {}).get("total"):
            bo.opening_weekend_gross = t["openingWeekendGross"]["gross"]["total"].get(
                "amount"
            )
            bo.opening_weekend_currency = t["openingWeekendGross"]["gross"][
                "total"
            ].get("currency")
            bo.opening_theaters = t["openingWeekendGross"].get("theaterCount")
        return bo

    async def get_title_company_credits(self, title_id: str) -> list[CompanyCreditItem]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_EXTRAS_QUERY, {"id": tid}, "GetExtras")
        items: list[CompanyCreditItem] = []
        for edge in data.get("title", {}).get("companyCredits", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(
                CompanyCreditItem(
                    category=n.get("category", {}).get("text"),
                    company_id=n.get("company", {}).get("id"),
                    company_name=n.get("company", {})
                    .get("companyText", {})
                    .get("text"),
                )
            )
        return items

    async def get_title_tech_specs(self, title_id: str) -> TechSpec:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_EXTRAS_QUERY, {"id": tid}, "GetExtras")
        ts_data = data.get("title", {}).get("technicalSpecifications", {})
        ts = TechSpec()
        for item in ts_data.get("aspectRatios", {}).get("items", []):
            if item.get("aspectRatio"):
                ts.aspect_ratios.append(item["aspectRatio"])
        for item in ts_data.get("soundMixes", {}).get("items", []):
            if item.get("text"):
                ts.sound_mixes.append(item["text"])
        for item in ts_data.get("colorations", {}).get("items", []):
            if item.get("text"):
                ts.colorations.append(item["text"])
        for item in ts_data.get("cameras", {}).get("items", []):
            if item.get("camera"):
                ts.cameras.append(item["camera"])
        return ts

    async def get_title_release_dates(self, title_id: str) -> list[ReleaseDateItem]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_EXTRAS_QUERY, {"id": tid}, "GetExtras")
        items: list[ReleaseDateItem] = []
        for edge in data.get("title", {}).get("releaseDates", {}).get("edges", []):
            n = edge.get("node", {})
            attrs = [
                a.get("text", "") for a in n.get("attributes", []) if a.get("text")
            ]
            items.append(
                ReleaseDateItem(
                    country=n.get("country", {}).get("text"),
                    day=n.get("day"),
                    month=n.get("month"),
                    year=n.get("year"),
                    attributes=attrs,
                )
            )
        return items

    async def get_title_parents_guide(self, title_id: str) -> list[ParentsGuideItem]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_EXTRAS_QUERY, {"id": tid}, "GetExtras")
        items: list[ParentsGuideItem] = []
        for edge in (
            data.get("title", {})
            .get("parentsGuide", {})
            .get("guideItems", {})
            .get("edges", [])
        ):
            n = edge.get("node", {})
            items.append(
                ParentsGuideItem(
                    category=n.get("category", {}).get("id"),
                    text=n.get("text", {}).get("markdown"),
                )
            )
        return items

    async def get_title_keywords(self, title_id: str) -> list[KeywordItem]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_EXTRAS_QUERY, {"id": tid}, "GetExtras")
        items: list[KeywordItem] = []
        for edge in data.get("title", {}).get("keywords", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(
                KeywordItem(
                    text=n.get("keyword", {}).get("text", {}).get("text"),
                    legacy_id=n.get("legacyId"),
                )
            )
        return items

    async def get_title_awards(self, title_id: str) -> list[AwardNomination]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_EXTRAS_QUERY, {"id": tid}, "GetExtras")
        items: list[AwardNomination] = []
        for edge in data.get("title", {}).get("awardNominations", {}).get("edges", []):
            n = edge.get("node", {})
            cat = n.get("category") or {}
            notes = n.get("notes")
            items.append(
                AwardNomination(
                    is_winner=n.get("isWinner", False),
                    award_name=(n.get("award") or {}).get("text"),
                    category=cat.get("text"),
                    notes=notes.get("markdown") if notes else None,
                )
            )
        return items

    async def get_title_watch_options(self, title_id: str) -> Optional[WatchOptionItem]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_EXTRAS_QUERY, {"id": tid}, "GetExtras")
        wo = data.get("title", {}).get("primaryWatchOption", {}).get("watchOption")
        if not wo:
            return None
        return WatchOptionItem(
            provider=wo.get("provider", {}).get("name", {}).get("value"),
            offer_type=wo.get("offerType"),
            link=wo.get("link"),
            description=wo.get("description", {}).get("value"),
        )

    async def get_title_plots(self, title_id: str) -> list[PlotSummary]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_INFO_QUERY, {"id": tid}, "GetInfo")
        items: list[PlotSummary] = []
        for edge in data.get("title", {}).get("plots", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(
                PlotSummary(
                    id=n.get("id"),
                    plot_type=n.get("plotType"),
                    text=n.get("plotText", {}).get("markdown"),
                    author=n.get("author"),
                    language=n.get("language", {}).get("text"),
                    is_spoiler=n.get("isSpoiler", False),
                )
            )
        return items

    async def get_title_images(self, title_id: str) -> list[TitleImage]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_INFO_QUERY, {"id": tid}, "GetInfo")
        items: list[TitleImage] = []
        for edge in data.get("title", {}).get("images", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(
                TitleImage(
                    id=n.get("id"),
                    url=n.get("url"),
                    width=n.get("width"),
                    height=n.get("height"),
                    caption=n.get("caption", {}).get("markdown"),
                    type=n.get("type"),
                )
            )
        return items

    async def get_title_soundtrack(self, title_id: str) -> list[SoundtrackTrack]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_INFO_QUERY, {"id": tid}, "GetInfo")
        items: list[SoundtrackTrack] = []
        for edge in data.get("title", {}).get("soundtrack", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(SoundtrackTrack(id=n.get("id"), text=n.get("text")))
        return items

    async def get_title_connections(self, title_id: str) -> list[TitleConnection]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_INFO_QUERY, {"id": tid}, "GetInfo")
        items: list[TitleConnection] = []
        for edge in data.get("title", {}).get("connections", {}).get("edges", []):
            n = edge.get("node", {})
            at = n.get("associatedTitle", {})
            items.append(
                TitleConnection(
                    category_id=n.get("category", {}).get("id"),
                    category_text=n.get("category", {}).get("text"),
                    title_id=at.get("id"),
                    title_name=at.get("titleText", {}).get("text"),
                    title_year=at.get("releaseYear", {}).get("year"),
                    description=n.get("description", {}).get("markdown"),
                )
            )
        return items

    async def get_title_akas(self, title_id: str) -> list[TitleAka]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_INFO_QUERY, {"id": tid}, "GetInfo")
        items: list[TitleAka] = []
        for edge in data.get("title", {}).get("akas", {}).get("edges", []):
            n = edge.get("node", {})
            attrs = [
                a.get("text", "") for a in n.get("attributes", []) if a.get("text")
            ]
            items.append(
                TitleAka(
                    text=n.get("text"),
                    country=n.get("country", {}).get("text"),
                    language=n.get("language", {}).get("text")
                    if n.get("language")
                    else None,
                    attributes=attrs,
                )
            )
        return items

    async def get_title_external_links(self, title_id: str) -> list[ExternalLink]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_INFO_QUERY, {"id": tid}, "GetInfo")
        items: list[ExternalLink] = []
        for edge in data.get("title", {}).get("externalLinks", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(
                ExternalLink(
                    url=n.get("url"),
                    label=n.get("label"),
                    category=n.get("externalLinkCategory", {}).get("text"),
                    category_id=n.get("externalLinkCategory", {}).get("id"),
                )
            )
        return items

    async def get_title_crazy_credits(self, title_id: str) -> list[CrazyCredit]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_DETAILS_QUERY, {"id": tid}, "GetDetails")
        items: list[CrazyCredit] = []
        for edge in data.get("title", {}).get("crazyCredits", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(
                CrazyCredit(id=n.get("id"), text=n.get("text", {}).get("markdown"))
            )
        return items

    async def get_title_faqs(self, title_id: str) -> list[FaqItem]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_DETAILS_QUERY, {"id": tid}, "GetDetails")
        items: list[FaqItem] = []
        for edge in data.get("title", {}).get("faqs", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(
                FaqItem(
                    id=n.get("id"),
                    question=n.get("question", {}).get("markdown"),
                    answer=n.get("answer", {}).get("markdown"),
                    is_spoiler=n.get("isSpoiler", False),
                )
            )
        return items

    async def get_title_news(self, title_id: str) -> list[NewsArticle]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_DETAILS_QUERY, {"id": tid}, "GetDetails")
        items: list[NewsArticle] = []
        for edge in data.get("title", {}).get("news", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(
                NewsArticle(
                    id=n.get("id"),
                    byline=n.get("byline"),
                    date=n.get("date"),
                    article_title=n.get("articleTitle", {}).get("markdown"),
                    url=n.get("externalUrl"),
                    image_url=n.get("image", {}).get("url"),
                )
            )
        return items

    async def get_title_certificate(self, title_id: str) -> Optional[CertificateInfo]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_DETAILS_QUERY, {"id": tid}, "GetDetails")
        cert = data.get("title", {}).get("certificate")
        if not cert:
            return None
        return CertificateInfo(
            rating=cert.get("rating"), country=cert.get("country", {}).get("text")
        )

    async def get_title_production_status(
        self, title_id: str
    ) -> Optional[ProductionStatusInfo]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_DETAILS_QUERY, {"id": tid}, "GetDetails")
        ps = (
            data.get("title", {})
            .get("productionStatus", {})
            .get("currentProductionStage")
        )
        if not ps:
            return None
        return ProductionStatusInfo(stage_id=ps.get("id"), stage_text=ps.get("text"))

    async def get_title_engagement_stats(self, title_id: str) -> EngagementStats:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_DETAILS_QUERY, {"id": tid}, "GetDetails")
        es = data.get("title", {}).get("engagementStatistics", {})
        ws = es.get("watchlistStatistics", {})
        fs = es.get("followerStatistics")
        return EngagementStats(
            watchlist_count=ws.get("totalCount", 0),
            watchlist_display=ws.get("displayableCount", {}).get("text"),
            follower_count=fs.get("totalCount", 0) if fs else 0,
            follower_display=fs.get("displayableCount", {}).get("text") if fs else None,
        )

    async def get_title_rating_histogram(
        self, title_id: str
    ) -> list[RatingHistogramEntry]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_DETAILS_QUERY, {"id": tid}, "GetDetails")
        items: list[RatingHistogramEntry] = []
        for entry in (
            data.get("title", {})
            .get("aggregateRatingsBreakdown", {})
            .get("histogram", {})
            .get("histogramValues", [])
        ):
            items.append(
                RatingHistogramEntry(
                    rating=entry.get("rating", 0), vote_count=entry.get("voteCount", 0)
                )
            )
        return items

    async def get_title_videos(self, title_id: str) -> list[TitleVideo]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_DETAILS_QUERY, {"id": tid}, "GetDetails")
        items: list[TitleVideo] = []
        for edge in data.get("title", {}).get("primaryVideos", {}).get("edges", []):
            n = edge.get("node", {})
            v = TitleVideo(
                id=n.get("id"),
                name=n.get("name", {}).get("value"),
                description=n.get("description", {}).get("value"),
                content_type=n.get("contentType", {}).get("id"),
                duration_seconds=n.get("runtime", {}).get("value"),
                thumbnail_url=n.get("thumbnail", {}).get("url"),
            )
            for u in n.get("playbackURLs", []):
                dn = u.get("displayName", {}).get("value")
                url = u.get("url")
                if dn and url:
                    v.playback_urls[dn] = url
            items.append(v)
        return items

    async def get_title_recommendations(self, title_id: str) -> list[Title]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(
            GET_TITLE_RECOMMENDATIONS_QUERY, {"id": tid}, "GetRecommendations"
        )
        titles: list[Title] = []
        for edge in (
            data.get("title", {}).get("moreLikeThisTitles", {}).get("edges", [])
        ):
            node = edge.get("node", {})
            t = Title(id=node.get("id"), title=node.get("titleText", {}).get("text"))
            t.title_type = node.get("titleType", {}).get("text")
            t.release_year = node.get("releaseYear", {}).get("year")
            t.poster_url = node.get("primaryImage", {}).get("url")
            rs = node.get("ratingsSummary")
            if rs:
                t.rating = Rating(aggregate_rating=rs.get("aggregateRating") or 0.0)
            titles.append(t)
        return titles

    async def get_title_meta(self, title_id: str) -> TitleMeta:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_META_QUERY, {"id": tid}, "GetMeta")
        m = data.get("title", {}).get("meta", {})
        return TitleMeta(canonical_id=m.get("canonicalId"))

    async def get_title_interests(self, title_id: str) -> list[InterestItem]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_META_QUERY, {"id": tid}, "GetMeta")
        items: list[InterestItem] = []
        for edge in data.get("title", {}).get("interests", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(
                InterestItem(
                    id=n.get("id"),
                    text=n.get("primaryText", {}).get("text"),
                    score=n.get("score", {}).get("currentScore", 0),
                )
            )
        return items

    async def get_title_related_lists(self, title_id: str) -> list[RelatedList]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_META_QUERY, {"id": tid}, "GetMeta")
        items: list[RelatedList] = []
        for edge in data.get("title", {}).get("relatedLists", {}).get("edges", []):
            n = edge.get("node", {})
            desc = n.get("description")
            items.append(
                RelatedList(
                    id=n.get("id"),
                    name=n.get("name", {}).get("originalText"),
                    description=desc.get("originalText", {}).get("markdown")
                    if desc
                    else None,
                )
            )
        return items

    async def _fetch_name_details(self, name_id: str) -> dict:
        nid = name_id if name_id.startswith("nm") else f"nm{name_id}"
        data = await self._graphql(
            GET_NAME_DETAILS_QUERY, {"id": nid}, "GetNameDetails"
        )
        return data.get("name") or {}

    async def get_name_height(self, name_id: str) -> Optional[NameHeight]:
        data = await self._fetch_name_details(name_id)
        h = data.get("height")
        if not h or not h.get("measurement"):
            return None
        return NameHeight(
            value_cm=h["measurement"].get("value"),
            display=h.get("displayableProperty", {}).get("value", {}).get("plainText"),
        )

    async def get_name_age(self, name_id: str) -> Optional[NameAge]:
        data = await self._fetch_name_details(name_id)
        a = data.get("age")
        if not a:
            return None
        return NameAge(value=a.get("value"), text=a.get("text"))

    async def get_name_birth_details(self, name_id: str) -> NameBirthDetails:
        data = await self._fetch_name_details(name_id)
        return NameBirthDetails(
            location=data.get("birthLocation", {}).get("text"),
            birth_name=data.get("birthName", {}).get("text"),
        )

    async def get_name_death_details(self, name_id: str) -> NameDeathDetails:
        data = await self._fetch_name_details(name_id)
        dl = data.get("deathLocation")
        dc = data.get("deathCause")
        return NameDeathDetails(
            location=dl.get("text") if dl else None,
            cause=dc.get("text") if dc else None,
        )

    async def get_name_spouses(self, name_id: str) -> list[NameSpouse]:
        data = await self._fetch_name_details(name_id)
        items: list[NameSpouse] = []
        for s in data.get("spouses", []):
            sp = s.get("spouse", {})
            name_node = sp.get("name", {})
            items.append(
                NameSpouse(
                    spouse_id=name_node.get("id"),
                    spouse_name=name_node.get("nameText", {}).get("text"),
                    is_current=s.get("current", False),
                )
            )
        return items

    async def get_name_awards(self, name_id: str) -> list[NameAward]:
        data = await self._fetch_name_details(name_id)
        items: list[NameAward] = []
        for edge in data.get("awardNominations", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(
                NameAward(
                    is_winner=n.get("isWinner", False),
                    award_name=n.get("award", {}).get("text"),
                    category=n.get("category", {}).get("text"),
                )
            )
        return items

    async def get_name_images(self, name_id: str) -> list[TitleImage]:
        data = await self._fetch_name_details(name_id)
        items: list[TitleImage] = []
        for edge in data.get("images", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(
                TitleImage(
                    id=n.get("id"),
                    url=n.get("url"),
                    width=n.get("width"),
                    height=n.get("height"),
                    type=n.get("type"),
                )
            )
        return items

    async def get_name_credits(self, name_id: str) -> list[NameCredit]:
        data = await self._fetch_name_details(name_id)
        items: list[NameCredit] = []
        for edge in data.get("credits", {}).get("edges", []):
            n = edge.get("node", {})
            t = n.get("title", {})
            items.append(
                NameCredit(
                    category=n.get("category", {}).get("text"),
                    title_id=t.get("id"),
                    title_name=t.get("titleText", {}).get("text"),
                )
            )
        return items

    async def get_name_other_works(self, name_id: str) -> list[NameOtherWork]:
        data = await self._fetch_name_details(name_id)
        items: list[NameOtherWork] = []
        for edge in data.get("otherWorks", {}).get("edges", []):
            n = edge.get("node", {})
            cat = n.get("category")
            items.append(
                NameOtherWork(
                    text=n.get("text", {}).get("markdown"),
                    category=cat.get("text") if cat else None,
                )
            )
        return items

    async def get_name_trivia(self, name_id: str) -> list[NameTriviaItem]:
        data = await self._fetch_name_details(name_id)
        items: list[NameTriviaItem] = []
        for edge in data.get("trivia", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(
                NameTriviaItem(id=n.get("id"), text=n.get("text", {}).get("markdown"))
            )
        return items

    async def get_name_quotes(self, name_id: str) -> list[NameQuoteItem]:
        data = await self._fetch_name_details(name_id)
        items: list[NameQuoteItem] = []
        for edge in data.get("quotes", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(
                NameQuoteItem(id=n.get("id"), text=n.get("text", {}).get("markdown"))
            )
        return items

    async def get_name_trademarks(self, name_id: str) -> list[NameTrademark]:
        data = await self._fetch_name_details(name_id)
        items: list[NameTrademark] = []
        for edge in data.get("trademarks", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(NameTrademark(text=n.get("text", {}).get("markdown")))
        return items

    async def get_name_known_for(self, name_id: str, first: int = 12) -> list[Title]:
        nid = name_id if name_id.startswith("nm") else f"nm{name_id}"
        data = await self._graphql(
            GET_NAME_KNOWN_FOR_QUERY, {"id": nid, "first": first}, "GetNameKnownFor"
        )
        name_node = data.get("name", {})
        results: list[Title] = []
        for edge in name_node.get("knownFor", {}).get("edges", []):
            t = edge.get("node", {}).get("title", {})
            if not t.get("id"):
                continue
            title = Title(id=t.get("id"), title=t.get("titleText", {}).get("text"))
            title.title_type = t.get("titleType", {}).get("text")
            title.release_year = t.get("releaseYear", {}).get("year")
            title.poster_url = t.get("primaryImage", {}).get("url")
            rs = t.get("ratingsSummary")
            if rs:
                title.rating = Rating(aggregate_rating=rs.get("aggregateRating") or 0.0)
            results.append(title)
        return results

    async def get_name_filmography_titles(
        self, name_id: str, first: int = 25
    ) -> list[Title]:
        n = await self.get_name(name_id)
        if not n:
            return []
        return n.filmography[:first]

    async def close(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
