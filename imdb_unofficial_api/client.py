import httpx
from typing import Optional, Any
from .models import Title, Name, SearchResult, Rating, Credit

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

ADVANCED_SEARCH_QUERY = """
query AdvancedSearch($query: String!, $first: Int!) {
  advancedTitleSearch(query: $query, first: $first) {
    edges {
      node {
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

    def _graphql(
        self, query: str, variables: dict[str, Any], operation_name: Optional[str] = None
    ) -> dict:
        payload: dict[str, Any] = {
            "query": query,
            "variables": variables,
        }
        if operation_name:
            payload["operationName"] = operation_name

        resp = self._client.post(GRAPHQL_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()

        if "errors" in data:
            raise RuntimeError(f"GraphQL error: {data['errors']}")

        return data.get("data", {})

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

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
