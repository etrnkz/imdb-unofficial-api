from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Rating:
    aggregate_rating: float = 0.0
    vote_count: int = 0
    top_rank: Optional[int] = None


@dataclass
class TitleText:
    text: Optional[str] = None


@dataclass
class ReleaseYear:
    year: Optional[int] = None
    end_year: Optional[int] = None


@dataclass
class Credit:
    person_id: Optional[str] = None
    name: Optional[str] = None
    characters: list[str] = field(default_factory=list)
    category: Optional[str] = None
    attributes: list[str] = field(default_factory=list)
    image_url: Optional[str] = None


@dataclass
class EpisodeInfo:
    season_number: Optional[str] = None
    episode_number: Optional[str] = None
    text: Optional[str] = None


@dataclass
class Title:
    id: Optional[str] = None
    title: Optional[str] = None
    original_title: Optional[str] = None
    title_type: Optional[str] = None
    release_year: Optional[int] = None
    end_year: Optional[int] = None
    rating: Optional[Rating] = None
    plot_outline: Optional[str] = None
    runtime_minutes: Optional[int] = None
    genres: list[str] = field(default_factory=list)
    countries: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    poster_url: Optional[str] = None
    popularity_rank: Optional[int] = None
    directors: list[Credit] = field(default_factory=list)
    writers: list[Credit] = field(default_factory=list)
    cast: list[Credit] = field(default_factory=list)
    recommendations: list["Title"] = field(default_factory=list)
    taglines: list[str] = field(default_factory=list)
    episode_info: Optional[EpisodeInfo] = None
    raw: Optional[dict] = None


@dataclass
class Season:
    season_number: Optional[str] = None
    text: Optional[str] = None


@dataclass
class Name:
    id: Optional[str] = None
    name: Optional[str] = None
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    bio: Optional[str] = None
    image_url: Optional[str] = None
    filmography: list[Title] = field(default_factory=list)
    raw: Optional[dict] = None


@dataclass
class UserReview:
    id: Optional[str] = None
    author: Optional[str] = None
    author_rating: Optional[int] = None
    summary: Optional[str] = None
    text: Optional[str] = None
    spoiler: bool = False
    up_votes: int = 0
    down_votes: int = 0
    helpfulness_score: Optional[int] = None
    submission_date: Optional[str] = None


@dataclass
class MetacriticReview:
    score: Optional[int] = None
    reviewer: Optional[str] = None
    quote: Optional[str] = None
    site: Optional[str] = None
    url: Optional[str] = None


@dataclass
class SearchResult:
    id: Optional[str] = None
    title: Optional[str] = None
    original_title: Optional[str] = None
    title_type: Optional[str] = None
    year: Optional[int] = None
    image_url: Optional[str] = None
    rating: Optional[float] = None
