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
class Trailer:
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[str] = None
    duration_seconds: Optional[int] = None
    thumbnail_url: Optional[str] = None
    playback_urls: dict[str, str] = field(default_factory=dict)


@dataclass
class TriviaItem:
    text: Optional[str] = None


@dataclass
class QuoteItem:
    text: Optional[str] = None


@dataclass
class GoofItem:
    text: Optional[str] = None
    category: Optional[str] = None


@dataclass
class BoxOffice:
    budget: Optional[int] = None
    budget_currency: Optional[str] = None
    lifetime_gross: Optional[int] = None
    lifetime_currency: Optional[str] = None
    opening_weekend_gross: Optional[int] = None
    opening_weekend_currency: Optional[str] = None
    opening_theaters: Optional[int] = None


@dataclass
class CompanyCreditItem:
    category: Optional[str] = None
    company_id: Optional[str] = None
    company_name: Optional[str] = None


@dataclass
class TechSpec:
    aspect_ratios: list[str] = field(default_factory=list)
    sound_mixes: list[str] = field(default_factory=list)
    colorations: list[str] = field(default_factory=list)
    cameras: list[str] = field(default_factory=list)


@dataclass
class ReleaseDateItem:
    country: Optional[str] = None
    day: Optional[int] = None
    month: Optional[int] = None
    year: Optional[int] = None
    attributes: list[str] = field(default_factory=list)


@dataclass
class ParentsGuideItem:
    category: Optional[str] = None
    text: Optional[str] = None


@dataclass
class KeywordItem:
    text: Optional[str] = None
    legacy_id: Optional[str] = None


@dataclass
class AwardNomination:
    is_winner: bool = False
    award_name: Optional[str] = None
    category: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class WatchOptionItem:
    provider: Optional[str] = None
    offer_type: Optional[str] = None
    link: Optional[str] = None
    description: Optional[str] = None


@dataclass
class PlotSummary:
    id: Optional[str] = None
    plot_type: Optional[str] = None
    text: Optional[str] = None
    author: Optional[str] = None
    language: Optional[str] = None
    is_spoiler: bool = False


@dataclass
class TitleImage:
    id: Optional[str] = None
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    caption: Optional[str] = None
    type: Optional[str] = None


@dataclass
class SoundtrackTrack:
    id: Optional[str] = None
    text: Optional[str] = None


@dataclass
class TitleConnection:
    category_id: Optional[str] = None
    category_text: Optional[str] = None
    title_id: Optional[str] = None
    title_name: Optional[str] = None
    title_year: Optional[int] = None
    description: Optional[str] = None


@dataclass
class TitleAka:
    text: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    attributes: list[str] = field(default_factory=list)


@dataclass
class ExternalLink:
    url: Optional[str] = None
    label: Optional[str] = None
    category: Optional[str] = None
    category_id: Optional[str] = None


@dataclass
class CrazyCredit:
    id: Optional[str] = None
    text: Optional[str] = None


@dataclass
class FaqItem:
    id: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    is_spoiler: bool = False


@dataclass
class NewsArticle:
    id: Optional[str] = None
    byline: Optional[str] = None
    date: Optional[str] = None
    article_title: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None


@dataclass
class CertificateInfo:
    rating: Optional[str] = None
    country: Optional[str] = None


@dataclass
class ProductionStatusInfo:
    stage_id: Optional[str] = None
    stage_text: Optional[str] = None


@dataclass
class EngagementStats:
    watchlist_count: int = 0
    watchlist_display: Optional[str] = None
    follower_count: int = 0
    follower_display: Optional[str] = None


@dataclass
class RatingHistogramEntry:
    rating: int = 0
    vote_count: int = 0


@dataclass
class TitleVideo:
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[str] = None
    duration_seconds: Optional[int] = None
    thumbnail_url: Optional[str] = None
    playback_urls: dict[str, str] = field(default_factory=dict)


@dataclass
class SearchResult:
    id: Optional[str] = None
    title: Optional[str] = None
    original_title: Optional[str] = None
    title_type: Optional[str] = None
    year: Optional[int] = None
    image_url: Optional[str] = None
    rating: Optional[float] = None
