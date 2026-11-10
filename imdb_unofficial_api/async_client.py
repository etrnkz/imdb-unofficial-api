import httpx
from typing import Optional, Any
from .models import Title, Name, SearchResult, Rating, Credit, Season, EpisodeInfo, UserReview, MetacriticReview

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
    GET_TITLE_QUERY, SEARCH_QUERY, GET_NAME_QUERY,
    GET_TITLE_FULL_CREDITS_QUERY, GET_TITLE_CREDITS_BY_CATEGORY,
    GET_TITLE_SEASONS_QUERY, GET_TITLE_EPISODES_QUERY,
    GET_TITLE_REVIEWS_QUERY, ADVANCED_SEARCH_QUERY_BASE,
)


class AsyncImdbClient:
    def __init__(
        self,
        country: Optional[str] = "US",
        language: Optional[str] = "en-US",
        timeout: float = 30.0,
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

    async def _graphql(
        self, query: str, variables: dict[str, Any], operation_name: Optional[str] = None
    ) -> dict:
        payload: dict[str, Any] = {"query": query, "variables": variables}
        if operation_name:
            payload["operationName"] = operation_name
        resp = await self._client.post(GRAPHQL_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()
        if "errors" in data:
            raise RuntimeError(f"GraphQL error: {data['errors']}")
        return data.get("data", {})

    async def get_title(self, title_id: str) -> Optional[Title]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_QUERY, {"id": tid}, "GetTitle")
        title_data = data.get("title")
        if not title_data:
            return None
        from .client import ImdbClient
        return ImdbClient._parse_title(None, title_data)

    async def search(self, query: str, first: int = 20) -> list[SearchResult]:
        data = await self._graphql(SEARCH_QUERY, {"searchTerm": query, "first": first}, "Search")
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
        return results

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
        constraints_parts: list[str] = []
        if query:
            constraints_parts.append(f'titleTextConstraint: {{searchTerm: "{query}", useFuzzySearch: true}}')
        if title_type:
            constraints_parts.append(f'titleTypeConstraint: {{anyTitleTypeIds: "{title_type}"}}')
        if genre_ids:
            constraints_parts.append(f'genreConstraint: {{anyGenreIds: "{genre_ids}"}}')
        if min_rating is not None:
            constraints_parts.append(f'userRatingsConstraint: {{aggregateRatingRange: {{min: {min_rating}}}}}')
        if release_date_start or release_date_end:
            d = []
            if release_date_start: d.append(f'start: "{release_date_start}"')
            if release_date_end: d.append(f'end: "{release_date_end}"')
            constraints_parts.append(f'releaseDateConstraint: {{releaseDateRange: {{{",".join(d)}}}}}')
        if min_runtime is not None or max_runtime is not None:
            d = []
            if min_runtime is not None: d.append(f'min: {min_runtime}')
            if max_runtime is not None: d.append(f'max: {max_runtime}')
            constraints_parts.append(f'runtimeConstraint: {{runtimeRangeMinutes: {{{",".join(d)}}}}}')

        if constraints_parts:
            constraints_str = ", constraints:{" + ",".join(constraints_parts) + "}"
            query_str = ADVANCED_SEARCH_QUERY_BASE.replace("{CONSTRAINTS}", constraints_str)
        else:
            query_str = ADVANCED_SEARCH_QUERY_BASE.replace("{CONSTRAINTS}", "")

        data = await self._graphql(query_str, {"first": first}, "AdvancedSearch")
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
        return results

    async def get_name(self, name_id: str) -> Optional[Name]:
        nid = name_id if name_id.startswith("nm") else f"nm{name_id}"
        data = await self._graphql(GET_NAME_QUERY, {"id": nid}, "GetName")
        name_data = data.get("name")
        if not name_data:
            return None
        from .client import ImdbClient
        return ImdbClient._parse_name(None, name_data)

    async def get_title_cast(self, title_id: str, category: Optional[str] = None) -> list[Credit]:
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
                c.characters = [ch.get("name", "") for ch in node["characters"] if ch.get("name")]
            if node.get("attributes"):
                c.attributes = [attr.get("text", "") for attr in node["attributes"] if attr.get("text")]
            credits.append(c)
        return credits

    async def get_title_seasons(self, title_id: str) -> list[Season]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = await self._graphql(GET_TITLE_SEASONS_QUERY, {"id": tid}, "GetSeasons")
        seasons: list[Season] = []
        for edge in data.get("title", {}).get("episodes", {}).get("displayableSeasons", {}).get("edges", []):
            node = edge.get("node", {})
            seasons.append(Season(season_number=node.get("season"), text=node.get("text")))
        return seasons

    async def get_title_episodes(self, title_id: str, season: Optional[str] = None, first: int = 50) -> list[Title]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        seasons_filter = [season] if season else ["1"]
        data = await self._graphql(
            GET_TITLE_EPISODES_QUERY,
            {"id": tid, "first": first, "seasons": seasons_filter},
            "GetEpisodes",
        )
        episodes: list[Title] = []
        for edge in data.get("title", {}).get("episodes", {}).get("episodes", {}).get("edges", []):
            node = edge.get("node", {})
            t = Title(
                id=node.get("id"),
                title=node.get("titleText", {}).get("text"),
                release_year=node.get("releaseYear", {}).get("year"),
                poster_url=node.get("primaryImage", {}).get("url"),
            )
            if node.get("ratingsSummary"):
                t.rating = Rating(
                    aggregate_rating=node["ratingsSummary"].get("aggregateRating") or 0.0,
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

    async def get_title_reviews(self, title_id: str) -> tuple[list[UserReview], list[MetacriticReview], Optional[int]]:
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
            metacritic_reviews.append(MetacriticReview(
                score=n.get("score"), reviewer=n.get("reviewer"),
                quote=n.get("quote", {}).get("value"), site=n.get("site"), url=n.get("url"),
            ))
        user_reviews: list[UserReview] = []
        for edge in title_data.get("reviews", {}).get("edges", []):
            n = edge.get("node", {})
            h = n.get("helpfulness", {})
            user_reviews.append(UserReview(
                id=n.get("id"), author=n.get("author", {}).get("username", {}).get("text"),
                author_rating=n.get("authorRating"), summary=n.get("summary", {}).get("originalText"),
                text=n.get("text", {}).get("originalText", {}).get("markdown"),
                spoiler=n.get("spoiler", False), up_votes=h.get("upVotes", 0),
                down_votes=h.get("downVotes", 0), helpfulness_score=h.get("score"),
                submission_date=n.get("submissionDate"),
            ))
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
        return [ImdbClient._parse_chart_title(None, edge.get("node", {})) for edge in data.get("chartTitles", {}).get("edges", [])]

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
        return [ImdbClient._parse_chart_title(None, node) for node in data.get("trendingTitles", {}).get("titles", [])]

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
        return [ImdbClient._parse_chart_title(None, node) for node in data.get("popularTitles", {}).get("titles", [])]

    async def close(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
