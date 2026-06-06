import httpx
import time
import functools
from typing import Optional, Any
from .models import Title, Name, SearchResult, Rating, Credit, Season, EpisodeInfo, UserReview, MetacriticReview, Trailer, TriviaItem, QuoteItem, GoofItem, BoxOffice, CompanyCreditItem, TechSpec, ReleaseDateItem, ParentsGuideItem, KeywordItem, AwardNomination, WatchOptionItem, PlotSummary, TitleImage, SoundtrackTrack, TitleConnection, TitleAka, ExternalLink, CrazyCredit, FaqItem, NewsArticle, CertificateInfo, ProductionStatusInfo, EngagementStats, RatingHistogramEntry, TitleVideo, TitleMeta, InterestItem, RelatedList, NameHeight, NameAge, NameBirthDetails, NameDeathDetails, NameSpouse, NameAward, NameCredit, NameOtherWork, NameTriviaItem, NameQuoteItem, NameTrademark

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

GET_TITLE_QUERY = """
query GetTitle($id: ID!) {
  title(id: $id) {
    id
    titleText { text }
    originalTitleText { text }
    titleType { text }
    releaseYear { year endYear }
    ratingsSummary {
      aggregateRating
      voteCount
      topRanking { rank }
    }
    plot { plotText { plainText } }
    primaryImage { url width height }
    meterRanking { currentRank rankChange { changeDirection difference } }
    runtimes(first: 5) { edges { node { seconds attributes { text } country { text } } } }
    titleGenres { genres { genre { text } subGenres { keyword { text { text } } } } }
    countriesOfOrigin { countries { id text } }
    spokenLanguages { spokenLanguages { id text } }
    taglines(first: 20) { edges { node { text } } }
    moreLikeThisTitles(first: 12) {
      edges {
        node {
          id
          titleText { text }
          ratingsSummary { aggregateRating }
          primaryImage { url width height }
          releaseYear { year }
        }
      }
    }
    series {
      displayableEpisodeNumber {
        episodeNumber { episodeNumber text }
        displayableSeason { season text }
      }
    }
    principalCredits {
      credits(limit: 5) {
        name { nameText { text } id primaryImage { url width height } }
        category { text }
      }
    }
  }
}
"""

SEARCH_QUERY = """
query Search($searchTerm: String!, $first: Int!) {
  mainSearch(first: $first, options: {searchTerm: $searchTerm, type: TITLE, includeAdult: true}) {
    edges {
      node {
        entity {
          ... on Title {
            id
            titleText { text }
            originalTitleText { text }
            titleType { text }
            releaseYear { year }
            primaryImage { url width height }
            ratingsSummary { aggregateRating }
          }
        }
      }
    }
  }
}
"""

PERSON_SEARCH_QUERY = """
query SearchPerson($searchTerm: String!, $first: Int!) {
  mainSearch(first: $first, options: {searchTerm: $searchTerm, type: NAME, includeAdult: true}) {
    edges {
      node {
        entity {
          ... on Name {
            id
            nameText { text }
            primaryImage { url width height }
          }
        }
      }
    }
  }
}
"""

GET_NAME_QUERY = """
query GetName($id: ID!) {
  name(id: $id) {
    id
    nameText { text }
    primaryImage { url width height }
    birthDate {
      dateComponents { day month year }
    }
    deathDate {
      dateComponents { day month year }
    }
    bios(first: 5) {
      edges {
        node {
          text { plainText }
        }
      }
    }
    knownFor(first: 20) {
      edges {
        node {
          ... on NameKnownFor {
            title {
              id
              titleText { text }
              titleType { text }
              releaseYear { year }
              ratingsSummary { aggregateRating }
            }
          }
        }
      }
    }
  }
}
"""

GET_NAME_DETAILS_QUERY = """
query GetNameDetails($id: ID!) {
  name(id: $id) {
    id
    height { measurement { value unit } displayableProperty { value { plainText } } }
    age { value text }
    birthLocation { text }
    deathLocation { text }
    deathCause { text }
    birthName { text }
    spouses { spouse { name { nameText { text } id } } current }
    awardNominations(first: 20) { edges { node { isWinner award { text } category { text } } } }
    images(first: 20) { edges { node { url width height type } } }
    credits(first: 50) {
      edges {
        node {
          ... on Credit {
            category { text }
            title { id titleText { text } }
          }
        }
      }
    }
    otherWorks(first: 20) { edges { node { text { markdown } category { id text } } } }
    trivia(first: 20) { edges { node { text { markdown } id } } }
    quotes(first: 20) { edges { node { text { markdown } id } } }
    trademarks(first: 20) { edges { node { text { markdown } } } }
  }
}
"""

ADVANCED_SEARCH_QUERY_BASE = """
query AdvancedSearch($first: Int!) {
  advancedTitleSearch(first: $first{CONSTRAINTS}) {
    total
    edges {
      node {
        title {
          id
          titleText { text }
          originalTitleText { text }
          titleType { text }
          releaseYear { year }
          primaryImage { url }
          ratingsSummary { aggregateRating }
        }
      }
    }
  }
}
"""

GET_TITLE_FULL_CREDITS_QUERY = """
query GetFullCredits($id: ID!) {
  title(id: $id) {
    credits(first: 200) {
      edges {
        node {
          ... on Cast {
            name { nameText { text } id primaryImage { url width height } }
            characters { name }
            attributes { text }
          }
        }
      }
    }
  }
}
"""

GET_TITLE_SEASONS_QUERY = """
query GetSeasons($id: ID!) {
  title(id: $id) {
    episodes {
      displayableSeasons(first: 30) {
        total
        edges {
          node {
            season
            text
          }
        }
      }
    }
  }
}
"""

GET_TITLE_EPISODES_QUERY = """
query GetEpisodes($id: ID!, $first: Int!, $seasons: [String!]!) {
  title(id: $id) {
    episodes {
      episodes(first: $first, filter: {includeSeasons: $seasons}) {
        total
        edges {
          node {
            id
            titleText { text }
            releaseYear { year }
            ratingsSummary { aggregateRating voteCount }
            primaryImage { url }
            series {
              displayableEpisodeNumber {
                episodeNumber { episodeNumber text }
                displayableSeason { season text }
              }
            }
          }
        }
      }
    }
  }
}
"""

GET_TITLE_REVIEWS_QUERY = """
query GetReviews($id: ID!) {
  title(id: $id) {
    id
    titleText { text }
    reviewSummary {
      overall { long { value { markdown } } }
      positive { long { value { markdown } } }
      negative { long { value { markdown } } }
    }
    metacritic {
      metascore { score reviewCount }
      reviews(first: 20) {
        edges {
          node {
            score
            reviewer
            quote { value }
            site
            url
          }
        }
      }
    }
      reviews(first: 10) {
      total
      edges {
        node {
          id
          authorRating
          spoiler
          summary { originalText }
          text { originalText { markdown } }
          author { username { text } }
          helpfulness { upVotes downVotes score }
          submissionDate
        }
      }
    }
  }
}
"""

GET_TITLE_MEDIA_QUERY = """
query GetMedia($id: ID!) {
  title(id: $id) {
    id
    titleText { text }
    latestTrailer {
      id
      name { value }
      description { value }
      contentType { displayName { value } id }
      runtime { value unit }
      thumbnail { url width height }
      playbackURLs { url displayName { value } videoDefinition }
    }
    trivia(first: 20) {
      total
      edges {
        node {
          displayableArticle { body { markdown } }
        }
      }
    }
    quotes(first: 20) {
      total
      edges {
        node {
          displayableArticle { body { markdown } }
        }
      }
    }
    goofs(first: 20) {
      total
      edges {
        node {
          text { markdown }
          category { text }
        }
      }
    }
    filmingLocations(first: 20) {
      total
      edges {
        node {
          location
          text
          attributes { text }
        }
      }
    }
  }
}
"""

GET_TITLE_EXTRAS_QUERY = """
query GetExtras($id: ID!) {
  title(id: $id) {
    id
    productionBudget { budget { amount currency } }
    lifetimeGross(boxOfficeArea: DOMESTIC) { total { amount currency } }
    openingWeekendGross(boxOfficeArea: DOMESTIC) { gross { total { amount currency } } theaterCount }
    technicalSpecifications {
      aspectRatios { items { aspectRatio } }
      soundMixes { items { text } }
      colorations { items { text } }
      cameras { items { camera } }
    }
    releaseDates(first: 20) {
      edges {
        node {
          country { text }
          day month year
          attributes { text }
        }
      }
    }
    parentsGuide {
      guideItems(first: 20) {
        edges {
          node { category { id } text { markdown } }
        }
      }
    }
    keywords(first: 20) {
        edges {
        node { keyword { text { text } } legacyId }
      }
    }
    companyCredits(first: 20) {
      edges {
        node {
          category { text }
          company { id companyText { text } }
        }
      }
    }
    awardNominations(first: 20) {
      edges {
        node {
          isWinner
          award { text }
          category { text }
          notes { markdown }
        }
      }
    }
    primaryWatchOption(location: {postalCodeLocation: {postalCode: "10001", country: "US"}}) {
      watchOption {
        provider { name { value } }
        offerType
        link(platform: WEB)
        description { value }
      }
    }
  }
}
"""

GET_TITLE_RECOMMENDATIONS_QUERY = """
query GetRecommendations($id: ID!) {
  title(id: $id) {
    id
    moreLikeThisTitles(first: 20) {
      edges {
        node {
          id titleText { text } ratingsSummary { aggregateRating } primaryImage { url } releaseYear { year } titleType { text }
        }
      }
    }
  }
}
"""

GET_TITLE_META_QUERY = """
query GetMeta($id: ID!) {
  title(id: $id) {
    id
    meta { canonicalId }
    interests(first: 20) { edges { node { id primaryText { text } score { currentScore } } } }
    relatedLists(first: 20) { edges { node { id name { originalText } description { originalText { markdown } } } } }
  }
}
"""

GET_TITLE_DETAILS_QUERY = """
query GetDetails($id: ID!) {
  title(id: $id) {
    id
    crazyCredits(first: 10) { edges { node { id text { markdown } } } }
    faqs(first: 10) { edges { node { id question { markdown } answer { markdown } isSpoiler } } }
    news(first: 5) { edges { node { id byline date articleTitle { markdown } externalUrl image { url } } } }
    certificate { rating country { text } }
    productionStatus { currentProductionStage { id text } }
    engagementStatistics {
      watchlistStatistics { totalCount displayableCount { text } }
      followerStatistics { totalCount displayableCount { text } }
    }
    aggregateRatingsBreakdown { histogram { histogramValues { rating voteCount } } }
    primaryVideos(first: 10) {
      edges { node { id name { value } description { value } contentType { id } runtime { value } thumbnail { url } playbackURLs { url displayName { value } } } }
    }
  }
}
"""

GET_TITLE_INFO_QUERY = """
query GetInfo($id: ID!) {
  title(id: $id) {
    id
    plots(first: 5, includeAllLocales: true) {
      edges {
        node {
          id plotType plotText { markdown } author language { id text } isSpoiler
        }
      }
    }
    images(first: 20) {
      edges {
        node {
          id url width height caption { markdown } type
        }
      }
    }
    soundtrack(first: 20) {
      edges {
        node { text id }
      }
    }
    connections(first: 20) {
      edges {
        node {
          category { id text }
          associatedTitle { id titleText { text } releaseYear { year } }
          description { markdown }
        }
      }
    }
    akas(first: 20) {
      edges {
        node {
          text country { text } language { text } attributes { text }
        }
      }
    }
    externalLinks(first: 20) {
      edges {
        node {
          url label externalLinkCategory { id text }
        }
      }
    }
  }
}
"""

GET_TITLE_CREDITS_BY_CATEGORY = """
query GetCreditsByCategory($id: ID!, $category: String!) {
  title(id: $id) {
    credits(first: 50, filter: {categories: [$category]}) {
      edges {
        node {
          ... on Cast {
            name { nameText { text } id primaryImage { url width height } }
            characters { name }
            attributes { text }
          }
        }
      }
    }
  }
}
"""


class ImdbClient:
    def __init__(
        self,
        country: Optional[str] = "US",
        language: Optional[str] = "en-US",
        timeout: float = 30.0,
        max_retries: int = 3,
        cache_ttl: int = 0,
    ):
        self._client = httpx.Client(
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

    def _cache_key(self, query: str, variables: dict) -> str:
        return f"{query}|{variables}"

    def _graphql(
        self, query: str, variables: dict[str, Any], operation_name: Optional[str] = None
    ) -> dict:
        ck = self._cache_key(query, variables)
        if self._cache_ttl > 0 and ck in self._cache:
            ts, data = self._cache[ck]
            if time.time() - ts < self._cache_ttl:
                return data

        payload: dict[str, Any] = {
            "query": query,
            "variables": variables,
        }
        if operation_name:
            payload["operationName"] = operation_name

        for attempt in range(self._max_retries):
            resp = self._client.post(GRAPHQL_URL, json=payload)
            if resp.status_code == 429:
                wait = 2 ** attempt
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()

            if "errors" in data:
                is_retriable = any(
                    e.get("extensions", {}).get("code") in ("INTERNAL_ERROR", "TIMEOUT")
                    for e in data["errors"]
                )
                if is_retriable and attempt < self._max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(f"GraphQL error: {data['errors']}")

            result = data.get("data", {})
            if self._cache_ttl > 0:
                self._cache[ck] = (time.time(), result)
            return result

        raise RuntimeError("Max retries exceeded")

    def get_title(self, title_id: str) -> Optional[Title]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_QUERY, {"id": tid}, "GetTitle")
        title_data = data.get("title")
        if not title_data:
            return None
        return self._parse_title(title_data)

    def _parse_title(self, d: dict) -> Title:
        t = Title(id=d.get("id"), raw=d)

        if d.get("titleText"):
            t.title = d["titleText"].get("text")
        if d.get("originalTitleText"):
            t.original_title = d["originalTitleText"].get("text")
        if d.get("titleType"):
            t.title_type = d["titleType"].get("text")
        if d.get("releaseYear"):
            t.release_year = d["releaseYear"].get("year")
            t.end_year = d["releaseYear"].get("endYear")
        if d.get("plot") and d["plot"].get("plotText"):
            t.plot_outline = d["plot"]["plotText"].get("plainText")
        if d.get("primaryImage"):
            t.poster_url = d["primaryImage"].get("url")

        if d.get("ratingsSummary"):
            rs = d["ratingsSummary"]
            r = Rating(
                aggregate_rating=rs.get("aggregateRating") or 0.0,
                vote_count=rs.get("voteCount") or 0,
            )
            if rs.get("topRanking"):
                r.top_rank = rs["topRanking"].get("rank")
            t.rating = r

        if d.get("meterRanking"):
            t.popularity_rank = d["meterRanking"].get("currentRank")

        if d.get("runtimes") and d["runtimes"].get("edges"):
            for edge in d["runtimes"]["edges"]:
                seconds = edge.get("node", {}).get("seconds")
                if seconds:
                    t.runtime_minutes = seconds // 60
                    break

        if d.get("titleGenres") and d["titleGenres"].get("genres"):
            for g in d["titleGenres"]["genres"]:
                if g.get("genre") and g["genre"].get("text"):
                    t.genres.append(g["genre"]["text"])

        if d.get("countriesOfOrigin") and d["countriesOfOrigin"].get("countries"):
            for c in d["countriesOfOrigin"]["countries"]:
                if c.get("text"):
                    t.countries.append(c["text"])

        if d.get("spokenLanguages") and d["spokenLanguages"].get("spokenLanguages"):
            for lang in d["spokenLanguages"]["spokenLanguages"]:
                if lang.get("text"):
                    t.languages.append(lang["text"])

        if d.get("taglines") and d["taglines"].get("edges"):
            for edge in d["taglines"]["edges"]:
                if edge.get("node", {}).get("text"):
                    t.taglines.append(edge["node"]["text"])

        if d.get("moreLikeThisTitles") and d["moreLikeThisTitles"].get("edges"):
            for edge in d["moreLikeThisTitles"]["edges"]:
                node = edge.get("node", {})
                rec = Title(
                    id=node.get("id"),
                    title=node.get("titleText", {}).get("text"),
                    release_year=node.get("releaseYear", {}).get("year"),
                    poster_url=node.get("primaryImage", {}).get("url"),
                )
                if node.get("ratingsSummary"):
                    rec.rating = Rating(
                        aggregate_rating=node["ratingsSummary"].get("aggregateRating") or 0.0
                    )
                t.recommendations.append(rec)

        if d.get("series") and d["series"].get("displayableEpisodeNumber"):
            den = d["series"]["displayableEpisodeNumber"]
            ei = EpisodeInfo()
            if den.get("displayableSeason"):
                ei.season_number = den["displayableSeason"].get("season")
            if den.get("episodeNumber"):
                ei.episode_number = den["episodeNumber"].get("episodeNumber")
                ei.text = den["episodeNumber"].get("text")
            t.episode_info = ei

        if d.get("principalCredits"):
            for pc in d["principalCredits"]:
                if not pc.get("credits"):
                    continue
                for cred in pc["credits"]:
                    c = Credit(
                        person_id=cred.get("name", {}).get("id"),
                        name=cred.get("name", {}).get("nameText", {}).get("text"),
                        category=cred.get("category", {}).get("text"),
                        image_url=cred.get("name", {}).get("primaryImage", {}).get("url"),
                    )
                    category_lower = (c.category or "").lower()
                    if category_lower in ("director",):
                        t.directors.append(c)
                    elif category_lower in ("writer",):
                        t.writers.append(c)

        return t

    def get_titles(self, *ids: str) -> list[Title]:
        parts: list[str] = []
        title_ids: list[str] = []
        for i, tid in enumerate(ids):
            tid_norm = tid if tid.startswith("tt") else f"tt{tid}"
            title_ids.append(tid_norm)
            parts.append(
                f"t{i}: title(id: \"{tid_norm}\") {{ id titleText {{ text }} titleType {{ text }} "
                f"releaseYear {{ year }} ratingsSummary {{ aggregateRating }} primaryImage {{ url }} }}"
            )
        if not parts:
            return []
        q = "{{ {} }}".format(" ".join(parts))
        data = self._graphql(q, {})
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

    def get_names(self, *ids: str) -> list[Name]:
        parts: list[str] = []
        name_ids: list[str] = []
        for i, nid in enumerate(ids):
            nid_norm = nid if nid.startswith("nm") else f"nm{nid}"
            name_ids.append(nid_norm)
            parts.append(
                f"n{i}: name(id: \"{nid_norm}\") {{ id nameText {{ text }} primaryImage {{ url }} }}"
            )
        if not parts:
            return []
        q = "{{ {} }}".format(" ".join(parts))
        data = self._graphql(q, {})
        results: list[Name] = []
        for i in range(len(ids)):
            node = data.get(f"n{i}")
            if not node:
                continue
            n = Name(id=node.get("id"), name=node.get("nameText", {}).get("text"))
            n.image_url = node.get("primaryImage", {}).get("url")
            results.append(n)
        return results

    def search(self, query: str, first: int = 20) -> list[SearchResult]:
        data = self._graphql(SEARCH_QUERY, {"searchTerm": query, "first": first}, "Search")
        results: list[SearchResult] = []
        edges = data.get("mainSearch", {}).get("edges", [])
        for edge in edges:
            node = edge.get("node", {}).get("entity", {})
            if not node.get("id"):
                continue
            if node["id"].startswith("tt"):
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

    def search_advanced(
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
        data = self._graphql(query_str, {"first": first}, "AdvancedSearch")

        results: list[SearchResult] = []
        edges = data.get("advancedTitleSearch", {}).get("edges", [])
        for edge in edges:
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

    def search_person(self, query: str, first: int = 20) -> list[SearchResult]:
        data = self._graphql(PERSON_SEARCH_QUERY, {"searchTerm": query, "first": first}, "SearchPerson")
        results: list[SearchResult] = []
        edges = data.get("mainSearch", {}).get("edges", [])
        for edge in edges:
            node = edge.get("node", {}).get("entity", {})
            if not node.get("id"):
                continue
            results.append(SearchResult(
                id=node.get("id"),
                title=node.get("nameText", {}).get("text"),
                image_url=(node.get("primaryImage") or {}).get("url"),
            ))
        return results

    def get_name(self, name_id: str) -> Optional[Name]:
        nid = name_id if name_id.startswith("nm") else f"nm{name_id}"
        data = self._graphql(GET_NAME_QUERY, {"id": nid}, "GetName")
        name_data = data.get("name")
        if not name_data:
            return None
        return self._parse_name(name_data)

    def _parse_name(self, d: dict) -> Name:
        n = Name(id=d.get("id"), raw=d)
        if d.get("nameText"):
            n.name = d["nameText"].get("text")
        if d.get("primaryImage"):
            n.image_url = d["primaryImage"].get("url")
        if d.get("birthDate") and d["birthDate"].get("dateComponents"):
            bc = d["birthDate"]["dateComponents"]
            parts = []
            if bc.get("year"): parts.append(str(bc["year"]))
            if bc.get("month"): parts.append(str(bc["month"]))
            if bc.get("day"): parts.append(str(bc["day"]))
            n.birth_date = "-".join(parts)
        if d.get("deathDate") and d["deathDate"].get("dateComponents"):
            dc = d["deathDate"]["dateComponents"]
            parts = []
            if dc.get("year"): parts.append(str(dc["year"]))
            if dc.get("month"): parts.append(str(dc["month"]))
            if dc.get("day"): parts.append(str(dc["day"]))
            n.death_date = "-".join(parts)
        if d.get("bios") and d["bios"].get("edges"):
            for edge in d["bios"]["edges"]:
                if edge.get("node", {}).get("text", {}).get("plainText"):
                    n.bio = edge["node"]["text"]["plainText"]
                    break
        if d.get("knownFor") and d["knownFor"].get("edges"):
            for edge in d["knownFor"]["edges"]:
                node = edge.get("node", {}).get("title", {})
                if not node.get("id"):
                    continue
                title = Title(
                    id=node.get("id"),
                    title=node.get("titleText", {}).get("text"),
                    title_type=node.get("titleType", {}).get("text"),
                    release_year=node.get("releaseYear", {}).get("year"),
                )
                if node.get("ratingsSummary"):
                    title.rating = Rating(
                        aggregate_rating=node["ratingsSummary"].get("aggregateRating") or 0.0
                    )
                n.filmography.append(title)
        return n

    def get_title_cast(self, title_id: str, category: Optional[str] = None) -> list[Credit]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        if category:
            data = self._graphql(
                GET_TITLE_CREDITS_BY_CATEGORY,
                {"id": tid, "category": category},
                "GetCreditsByCategory",
            )
        else:
            data = self._graphql(
                GET_TITLE_FULL_CREDITS_QUERY,
                {"id": tid},
                "GetFullCredits",
            )
        credits: list[Credit] = []
        edges = data.get("title", {}).get("credits", {}).get("edges", [])
        for edge in edges:
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

    def get_title_seasons(self, title_id: str) -> list[Season]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_SEASONS_QUERY, {"id": tid}, "GetSeasons")
        seasons: list[Season] = []
        edges = data.get("title", {}).get("episodes", {}).get("displayableSeasons", {}).get("edges", [])
        for edge in edges:
            node = edge.get("node", {})
            seasons.append(Season(
                season_number=node.get("season"),
                text=node.get("text"),
            ))
        return seasons

    def get_title_episodes(
        self, title_id: str, season: Optional[str] = None, first: int = 50
    ) -> list[Title]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        seasons_filter = [season] if season else ["1"]
        data = self._graphql(
            GET_TITLE_EPISODES_QUERY,
            {"id": tid, "first": first, "seasons": seasons_filter},
            "GetEpisodes",
        )
        episodes: list[Title] = []
        edges = data.get("title", {}).get("episodes", {}).get("episodes", {}).get("edges", [])
        for edge in edges:
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

    def get_title_reviews(self, title_id: str) -> tuple[list[UserReview], list[MetacriticReview], Optional[int]]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_REVIEWS_QUERY, {"id": tid}, "GetReviews")
        title_data = data.get("title", {})

        metacritic_score: Optional[int] = None
        mc = title_data.get("metacritic", {})
        if mc.get("metascore"):
            metacritic_score = mc["metascore"].get("score")

        metacritic_reviews: list[MetacriticReview] = []
        for edge in mc.get("reviews", {}).get("edges", []):
            n = edge.get("node", {})
            metacritic_reviews.append(MetacriticReview(
                score=n.get("score"),
                reviewer=n.get("reviewer"),
                quote=n.get("quote", {}).get("value"),
                site=n.get("site"),
                url=n.get("url"),
            ))

        user_reviews: list[UserReview] = []
        for edge in title_data.get("reviews", {}).get("edges", []):
            n = edge.get("node", {})
            h = n.get("helpfulness", {})
            user_reviews.append(UserReview(
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
            ))

        return user_reviews, metacritic_reviews, metacritic_score

    def get_chart(self, chart_type: str, first: int = 50) -> list[Title]:
        query_str = """
query GetChart($first: Int!) {
  chartTitles(first: $first, chart: {chartType: CHART_TYPE}) {
    edges {
      node {
        id
        titleText { text }
        releaseYear { year }
        ratingsSummary { aggregateRating voteCount topRanking { rank } }
        primaryImage { url }
        titleType { text }
      }
    }
  }
}
""".replace("CHART_TYPE", chart_type)
        data = self._graphql(query_str, {"first": first}, "GetChart")
        return [self._parse_chart_title(edge.get("node", {})) for edge in data.get("chartTitles", {}).get("edges", [])]

    def _parse_chart_title(self, node: dict) -> Title:
        t = Title(id=node.get("id"))
        if node.get("titleText"):
            t.title = node["titleText"].get("text")
        if node.get("titleType"):
            t.title_type = node["titleType"].get("text")
        if node.get("releaseYear"):
            t.release_year = node["releaseYear"].get("year")
        if node.get("primaryImage"):
            t.poster_url = node["primaryImage"].get("url")
        if node.get("ratingsSummary"):
            rs = node["ratingsSummary"]
            t.rating = Rating(
                aggregate_rating=rs.get("aggregateRating") or 0.0,
                vote_count=rs.get("voteCount") or 0,
            )
            if rs.get("topRanking"):
                t.rating.top_rank = rs["topRanking"].get("rank")
        return t

    def get_trending(self, limit: int = 50) -> list[Title]:
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
        data = self._graphql(query_str, {"limit": limit})
        return [self._parse_chart_title(node) for node in data.get("trendingTitles", {}).get("titles", [])]

    def get_popular(self, limit: int = 50) -> list[Title]:
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
        data = self._graphql(query_str, {"limit": limit})
        return [self._parse_chart_title(node) for node in data.get("popularTitles", {}).get("titles", [])]

    def get_title_trailer(self, title_id: str) -> Optional[Trailer]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_MEDIA_QUERY, {"id": tid}, "GetMedia")
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

    def get_title_trivia(self, title_id: str) -> list[TriviaItem]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_MEDIA_QUERY, {"id": tid}, "GetMedia")
        items: list[TriviaItem] = []
        for edge in data.get("title", {}).get("trivia", {}).get("edges", []):
            body = edge.get("node", {}).get("displayableArticle", {}).get("body", {}).get("markdown")
            if body:
                items.append(TriviaItem(text=body))
        return items

    def get_title_quotes(self, title_id: str) -> list[QuoteItem]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_MEDIA_QUERY, {"id": tid}, "GetMedia")
        items: list[QuoteItem] = []
        for edge in data.get("title", {}).get("quotes", {}).get("edges", []):
            body = edge.get("node", {}).get("displayableArticle", {}).get("body", {}).get("markdown")
            if body:
                items.append(QuoteItem(text=body))
        return items

    def get_title_goofs(self, title_id: str) -> list[GoofItem]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_MEDIA_QUERY, {"id": tid}, "GetMedia")
        items: list[GoofItem] = []
        for edge in data.get("title", {}).get("goofs", {}).get("edges", []):
            n = edge.get("node", {})
            text = n.get("text", {}).get("markdown")
            cat = n.get("category", {}).get("text")
            if text:
                items.append(GoofItem(text=text, category=cat))
        return items

    def get_title_filming_locations(self, title_id: str) -> list[dict]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_MEDIA_QUERY, {"id": tid}, "GetMedia")
        items: list[dict] = []
        for edge in data.get("title", {}).get("filmingLocations", {}).get("edges", []):
            n = edge.get("node", {})
            attrs = [a.get("text", "") for a in n.get("attributes", []) if a.get("text")]
            items.append({
                "location": n.get("location"),
                "text": n.get("text"),
                "attributes": attrs,
            })
        return items

    def get_title_box_office(self, title_id: str) -> Optional[BoxOffice]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_EXTRAS_QUERY, {"id": tid}, "GetExtras")
        t = data.get("title", {})
        bo = BoxOffice()
        if t.get("productionBudget", {}).get("budget"):
            bo.budget = t["productionBudget"]["budget"].get("amount")
            bo.budget_currency = t["productionBudget"]["budget"].get("currency")
        if t.get("lifetimeGross", {}).get("total"):
            bo.lifetime_gross = t["lifetimeGross"]["total"].get("amount")
            bo.lifetime_currency = t["lifetimeGross"]["total"].get("currency")
        if t.get("openingWeekendGross", {}).get("gross", {}).get("total"):
            bo.opening_weekend_gross = t["openingWeekendGross"]["gross"]["total"].get("amount")
            bo.opening_weekend_currency = t["openingWeekendGross"]["gross"]["total"].get("currency")
            bo.opening_theaters = t["openingWeekendGross"].get("theaterCount")
        return bo

    def get_title_company_credits(self, title_id: str) -> list[CompanyCreditItem]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_EXTRAS_QUERY, {"id": tid}, "GetExtras")
        items: list[CompanyCreditItem] = []
        for edge in data.get("title", {}).get("companyCredits", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(CompanyCreditItem(
                category=n.get("category", {}).get("text"),
                company_id=n.get("company", {}).get("id"),
                company_name=n.get("company", {}).get("companyText", {}).get("text"),
            ))
        return items

    def get_title_tech_specs(self, title_id: str) -> TechSpec:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_EXTRAS_QUERY, {"id": tid}, "GetExtras")
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

    def get_title_release_dates(self, title_id: str) -> list[ReleaseDateItem]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_EXTRAS_QUERY, {"id": tid}, "GetExtras")
        items: list[ReleaseDateItem] = []
        for edge in data.get("title", {}).get("releaseDates", {}).get("edges", []):
            n = edge.get("node", {})
            attrs = [a.get("text", "") for a in n.get("attributes", []) if a.get("text")]
            items.append(ReleaseDateItem(
                country=n.get("country", {}).get("text"),
                day=n.get("day"),
                month=n.get("month"),
                year=n.get("year"),
                attributes=attrs,
            ))
        return items

    def get_title_parents_guide(self, title_id: str) -> list[ParentsGuideItem]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_EXTRAS_QUERY, {"id": tid}, "GetExtras")
        items: list[ParentsGuideItem] = []
        for edge in data.get("title", {}).get("parentsGuide", {}).get("guideItems", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(ParentsGuideItem(
                category=n.get("category", {}).get("id"),
                text=n.get("text", {}).get("markdown"),
            ))
        return items

    def get_title_keywords(self, title_id: str) -> list[KeywordItem]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_EXTRAS_QUERY, {"id": tid}, "GetExtras")
        items: list[KeywordItem] = []
        for edge in data.get("title", {}).get("keywords", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(KeywordItem(
                text=n.get("keyword", {}).get("text", {}).get("text"),
                legacy_id=n.get("legacyId"),
            ))
        return items

    def get_title_awards(self, title_id: str) -> list[AwardNomination]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_EXTRAS_QUERY, {"id": tid}, "GetExtras")
        items: list[AwardNomination] = []
        for edge in data.get("title", {}).get("awardNominations", {}).get("edges", []):
            n = edge.get("node", {})
            cat = n.get("category") or {}
            notes = n.get("notes")
            items.append(AwardNomination(
                is_winner=n.get("isWinner", False),
                award_name=(n.get("award") or {}).get("text"),
                category=cat.get("text"),
                notes=notes.get("markdown") if notes else None,
            ))
        return items

    def get_title_watch_options(self, title_id: str) -> Optional[WatchOptionItem]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_EXTRAS_QUERY, {"id": tid}, "GetExtras")
        wo = data.get("title", {}).get("primaryWatchOption", {}).get("watchOption")
        if not wo:
            return None
        return WatchOptionItem(
            provider=wo.get("provider", {}).get("name", {}).get("value"),
            offer_type=wo.get("offerType"),
            link=wo.get("link"),
            description=wo.get("description", {}).get("value"),
        )

    def get_title_plots(self, title_id: str) -> list[PlotSummary]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_INFO_QUERY, {"id": tid}, "GetInfo")
        items: list[PlotSummary] = []
        for edge in data.get("title", {}).get("plots", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(PlotSummary(
                id=n.get("id"),
                plot_type=n.get("plotType"),
                text=n.get("plotText", {}).get("markdown"),
                author=n.get("author"),
                language=n.get("language", {}).get("text"),
                is_spoiler=n.get("isSpoiler", False),
            ))
        return items

    def get_title_images(self, title_id: str) -> list[TitleImage]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_INFO_QUERY, {"id": tid}, "GetInfo")
        items: list[TitleImage] = []
        for edge in data.get("title", {}).get("images", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(TitleImage(
                id=n.get("id"),
                url=n.get("url"),
                width=n.get("width"),
                height=n.get("height"),
                caption=n.get("caption", {}).get("markdown"),
                type=n.get("type"),
            ))
        return items

    def get_title_soundtrack(self, title_id: str) -> list[SoundtrackTrack]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_INFO_QUERY, {"id": tid}, "GetInfo")
        items: list[SoundtrackTrack] = []
        for edge in data.get("title", {}).get("soundtrack", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(SoundtrackTrack(id=n.get("id"), text=n.get("text")))
        return items

    def get_title_connections(self, title_id: str) -> list[TitleConnection]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_INFO_QUERY, {"id": tid}, "GetInfo")
        items: list[TitleConnection] = []
        for edge in data.get("title", {}).get("connections", {}).get("edges", []):
            n = edge.get("node", {})
            at = n.get("associatedTitle", {})
            items.append(TitleConnection(
                category_id=n.get("category", {}).get("id"),
                category_text=n.get("category", {}).get("text"),
                title_id=at.get("id"),
                title_name=at.get("titleText", {}).get("text"),
                title_year=at.get("releaseYear", {}).get("year"),
                description=n.get("description", {}).get("markdown"),
            ))
        return items

    def get_title_akas(self, title_id: str) -> list[TitleAka]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_INFO_QUERY, {"id": tid}, "GetInfo")
        items: list[TitleAka] = []
        for edge in data.get("title", {}).get("akas", {}).get("edges", []):
            n = edge.get("node", {})
            attrs = [a.get("text", "") for a in n.get("attributes", []) if a.get("text")]
            items.append(TitleAka(
                text=n.get("text"),
                country=n.get("country", {}).get("text"),
                language=n.get("language", {}).get("text") if n.get("language") else None,
                attributes=attrs,
            ))
        return items

    def get_title_external_links(self, title_id: str) -> list[ExternalLink]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_INFO_QUERY, {"id": tid}, "GetInfo")
        items: list[ExternalLink] = []
        for edge in data.get("title", {}).get("externalLinks", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(ExternalLink(
                url=n.get("url"),
                label=n.get("label"),
                category=n.get("externalLinkCategory", {}).get("text"),
                category_id=n.get("externalLinkCategory", {}).get("id"),
            ))
        return items

    def get_title_crazy_credits(self, title_id: str) -> list[CrazyCredit]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_DETAILS_QUERY, {"id": tid}, "GetDetails")
        items: list[CrazyCredit] = []
        for edge in data.get("title", {}).get("crazyCredits", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(CrazyCredit(
                id=n.get("id"),
                text=n.get("text", {}).get("markdown"),
            ))
        return items

    def get_title_faqs(self, title_id: str) -> list[FaqItem]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_DETAILS_QUERY, {"id": tid}, "GetDetails")
        items: list[FaqItem] = []
        for edge in data.get("title", {}).get("faqs", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(FaqItem(
                id=n.get("id"),
                question=n.get("question", {}).get("markdown"),
                answer=n.get("answer", {}).get("markdown"),
                is_spoiler=n.get("isSpoiler", False),
            ))
        return items

    def get_title_news(self, title_id: str) -> list[NewsArticle]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_DETAILS_QUERY, {"id": tid}, "GetDetails")
        items: list[NewsArticle] = []
        for edge in data.get("title", {}).get("news", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(NewsArticle(
                id=n.get("id"),
                byline=n.get("byline"),
                date=n.get("date"),
                article_title=n.get("articleTitle", {}).get("markdown"),
                url=n.get("externalUrl"),
                image_url=n.get("image", {}).get("url"),
            ))
        return items

    def get_title_certificate(self, title_id: str) -> Optional[CertificateInfo]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_DETAILS_QUERY, {"id": tid}, "GetDetails")
        cert = data.get("title", {}).get("certificate")
        if not cert:
            return None
        return CertificateInfo(
            rating=cert.get("rating"),
            country=cert.get("country", {}).get("text"),
        )

    def get_title_production_status(self, title_id: str) -> Optional[ProductionStatusInfo]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_DETAILS_QUERY, {"id": tid}, "GetDetails")
        ps = data.get("title", {}).get("productionStatus", {}).get("currentProductionStage")
        if not ps:
            return None
        return ProductionStatusInfo(stage_id=ps.get("id"), stage_text=ps.get("text"))

    def get_title_engagement_stats(self, title_id: str) -> EngagementStats:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_DETAILS_QUERY, {"id": tid}, "GetDetails")
        es = data.get("title", {}).get("engagementStatistics", {})
        ws = es.get("watchlistStatistics", {})
        fs = es.get("followerStatistics")
        return EngagementStats(
            watchlist_count=ws.get("totalCount", 0),
            watchlist_display=ws.get("displayableCount", {}).get("text"),
            follower_count=fs.get("totalCount", 0) if fs else 0,
            follower_display=fs.get("displayableCount", {}).get("text") if fs else None,
        )

    def get_title_rating_histogram(self, title_id: str) -> list[RatingHistogramEntry]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_DETAILS_QUERY, {"id": tid}, "GetDetails")
        items: list[RatingHistogramEntry] = []
        for entry in data.get("title", {}).get("aggregateRatingsBreakdown", {}).get("histogram", {}).get("histogramValues", []):
            items.append(RatingHistogramEntry(
                rating=entry.get("rating", 0),
                vote_count=entry.get("voteCount", 0),
            ))
        return items

    def get_title_videos(self, title_id: str) -> list[TitleVideo]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_DETAILS_QUERY, {"id": tid}, "GetDetails")
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

    def get_title_recommendations(self, title_id: str) -> list[Title]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_RECOMMENDATIONS_QUERY, {"id": tid}, "GetRecommendations")
        titles: list[Title] = []
        for edge in data.get("title", {}).get("moreLikeThisTitles", {}).get("edges", []):
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

    def get_title_meta(self, title_id: str) -> TitleMeta:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_META_QUERY, {"id": tid}, "GetMeta")
        m = data.get("title", {}).get("meta", {})
        return TitleMeta(canonical_id=m.get("canonicalId"))

    def get_title_interests(self, title_id: str) -> list[InterestItem]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_META_QUERY, {"id": tid}, "GetMeta")
        items: list[InterestItem] = []
        for edge in data.get("title", {}).get("interests", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(InterestItem(
                id=n.get("id"),
                text=n.get("primaryText", {}).get("text"),
                score=n.get("score", {}).get("currentScore", 0),
            ))
        return items

    def get_title_related_lists(self, title_id: str) -> list[RelatedList]:
        tid = title_id if title_id.startswith("tt") else f"tt{title_id}"
        data = self._graphql(GET_TITLE_META_QUERY, {"id": tid}, "GetMeta")
        items: list[RelatedList] = []
        for edge in data.get("title", {}).get("relatedLists", {}).get("edges", []):
            n = edge.get("node", {})
            desc = n.get("description")
            items.append(RelatedList(
                id=n.get("id"),
                name=n.get("name", {}).get("originalText"),
                description=desc.get("originalText", {}).get("markdown") if desc else None,
            ))
        return items

    def _fetch_name_details(self, name_id: str) -> dict:
        nid = name_id if name_id.startswith("nm") else f"nm{name_id}"
        return self._graphql(GET_NAME_DETAILS_QUERY, {"id": nid}, "GetNameDetails")

    def get_name_height(self, name_id: str) -> Optional[NameHeight]:
        data = self._fetch_name_details(name_id).get("name", {})
        h = data.get("height")
        if not h or not h.get("measurement"):
            return None
        return NameHeight(
            value_cm=h["measurement"].get("value"),
            display=h.get("displayableProperty", {}).get("value", {}).get("plainText"),
        )

    def get_name_age(self, name_id: str) -> Optional[NameAge]:
        data = self._fetch_name_details(name_id).get("name", {})
        a = data.get("age")
        if not a:
            return None
        return NameAge(value=a.get("value"), text=a.get("text"))

    def get_name_birth_details(self, name_id: str) -> NameBirthDetails:
        data = self._fetch_name_details(name_id).get("name", {})
        return NameBirthDetails(
            location=data.get("birthLocation", {}).get("text"),
            birth_name=data.get("birthName", {}).get("text"),
        )

    def get_name_death_details(self, name_id: str) -> NameDeathDetails:
        data = self._fetch_name_details(name_id).get("name", {})
        dl = data.get("deathLocation")
        dc = data.get("deathCause")
        return NameDeathDetails(
            location=dl.get("text") if dl else None,
            cause=dc.get("text") if dc else None,
        )

    def get_name_spouses(self, name_id: str) -> list[NameSpouse]:
        data = self._fetch_name_details(name_id).get("name", {})
        items: list[NameSpouse] = []
        for s in data.get("spouses", []):
            sp = s.get("spouse", {})
            name_node = sp.get("name", {})
            items.append(NameSpouse(
                spouse_id=name_node.get("id"),
                spouse_name=name_node.get("nameText", {}).get("text"),
                is_current=s.get("current", False),
            ))
        return items

    def get_name_awards(self, name_id: str) -> list[NameAward]:
        data = self._fetch_name_details(name_id).get("name", {})
        items: list[NameAward] = []
        for edge in data.get("awardNominations", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(NameAward(
                is_winner=n.get("isWinner", False),
                award_name=n.get("award", {}).get("text"),
                category=n.get("category", {}).get("text"),
            ))
        return items

    def get_name_images(self, name_id: str) -> list[TitleImage]:
        data = self._fetch_name_details(name_id).get("name", {})
        items: list[TitleImage] = []
        for edge in data.get("images", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(TitleImage(
                id=n.get("id"), url=n.get("url"), width=n.get("width"),
                height=n.get("height"), type=n.get("type"),
            ))
        return items

    def get_name_credits(self, name_id: str) -> list[NameCredit]:
        data = self._fetch_name_details(name_id).get("name", {})
        items: list[NameCredit] = []
        for edge in data.get("credits", {}).get("edges", []):
            n = edge.get("node", {})
            t = n.get("title", {})
            items.append(NameCredit(
                category=n.get("category", {}).get("text"),
                title_id=t.get("id"),
                title_name=t.get("titleText", {}).get("text"),
            ))
        return items

    def get_name_other_works(self, name_id: str) -> list[NameOtherWork]:
        data = self._fetch_name_details(name_id).get("name", {})
        items: list[NameOtherWork] = []
        for edge in data.get("otherWorks", {}).get("edges", []):
            n = edge.get("node", {})
            cat = n.get("category")
            items.append(NameOtherWork(
                text=n.get("text", {}).get("markdown"),
                category=cat.get("text") if cat else None,
            ))
        return items

    def get_name_trivia(self, name_id: str) -> list[NameTriviaItem]:
        data = self._fetch_name_details(name_id).get("name", {})
        items: list[NameTriviaItem] = []
        for edge in data.get("trivia", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(NameTriviaItem(
                id=n.get("id"),
                text=n.get("text", {}).get("markdown"),
            ))
        return items

    def get_name_quotes(self, name_id: str) -> list[NameQuoteItem]:
        data = self._fetch_name_details(name_id).get("name", {})
        items: list[NameQuoteItem] = []
        for edge in data.get("quotes", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(NameQuoteItem(
                id=n.get("id"),
                text=n.get("text", {}).get("markdown"),
            ))
        return items

    def get_name_trademarks(self, name_id: str) -> list[NameTrademark]:
        data = self._fetch_name_details(name_id).get("name", {})
        items: list[NameTrademark] = []
        for edge in data.get("trademarks", {}).get("edges", []):
            n = edge.get("node", {})
            items.append(NameTrademark(text=n.get("text", {}).get("markdown")))
        return items

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
