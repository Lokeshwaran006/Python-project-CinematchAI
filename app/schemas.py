from datetime import date, datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class CastMember(BaseModel):
    name: str
    character: Optional[str] = None


class CrewMember(BaseModel):
    name: str
    job: str
    department: Optional[str] = None


class MovieBase(BaseModel):
    title: str = Field(..., max_length=300)
    original_title: Optional[str] = Field(None, max_length=300)
    overview: Optional[str] = None
    tagline: Optional[str] = None
    status: Optional[str] = "Released"
    release_date: Optional[date] = None
    vote_average: Optional[float] = Field(None, ge=0.0, le=10.0)
    vote_count: Optional[int] = Field(0, ge=0)
    popularity: Optional[float] = None
    budget: Optional[int] = None
    revenue: Optional[int] = None
    runtime: Optional[float] = None
    original_language: Optional[str] = Field(None, max_length=10)
    genres: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    production_companies: List[str] = Field(default_factory=list)
    production_countries: List[str] = Field(default_factory=list)
    director: Optional[str] = Field(None, max_length=200)
    cast_members: List[CastMember] = Field(default_factory=list)
    crew_members: List[CrewMember] = Field(default_factory=list)
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None


class MovieCreate(MovieBase):
    id: int = Field(..., description="Unique TMDB Movie ID")


class MovieUpdate(BaseModel):
    title: Optional[str] = None
    original_title: Optional[str] = None
    overview: Optional[str] = None
    tagline: Optional[str] = None
    status: Optional[str] = None
    release_date: Optional[date] = None
    vote_average: Optional[float] = Field(None, ge=0.0, le=10.0)
    vote_count: Optional[int] = Field(None, ge=0)
    popularity: Optional[float] = None
    budget: Optional[int] = None
    revenue: Optional[int] = None
    runtime: Optional[float] = None
    original_language: Optional[str] = None
    genres: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    production_companies: Optional[List[str]] = None
    production_countries: Optional[List[str]] = None
    director: Optional[str] = None
    cast_members: Optional[List[CastMember]] = None
    crew_members: Optional[List[CrewMember]] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None


class MovieCardOut(BaseModel):
    id: int
    title: str
    year: Optional[int] = None
    release_date: Optional[str] = None
    vote_average: Optional[float] = None
    vote_count: int = 0
    genres: List[str] = Field(default_factory=list)
    original_language: Optional[str] = "en"
    revenue: Optional[int] = None
    revenue_display: Optional[str] = None
    poster_url: str
    backdrop_url: Optional[str] = None
    director: Optional[str] = None
    cast: List[str] = Field(default_factory=list)
    match_percentage: Optional[int] = None
    is_in_watchlist: bool = False

    class Config:
        from_attributes = True


class MovieOut(MovieBase):
    id: int
    year: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_edited_by: Optional[str] = None
    poster_url: str
    backdrop_url: str
    rotten_tomatoes_pct: Optional[int] = None
    revenue_display: Optional[str] = None
    budget_display: Optional[str] = None
    is_in_watchlist: bool = False
    user_rating: Optional[float] = None

    class Config:
        from_attributes = True


class PaginatedMovies(BaseModel):
    total: int
    page: int
    limit: int
    pages: int
    items: List[MovieCardOut]


class RecommendationItem(BaseModel):
    id: int
    title: str
    year: Optional[int] = None
    vote_average: Optional[float] = None
    genres: List[str] = Field(default_factory=list)
    director: Optional[str] = None
    poster_url: str
    match_percentage: int
    rationale_tags: List[str] = Field(default_factory=list)
    primary_reason: str


class RecommendationResponse(BaseModel):
    query_movie_id: int
    query_movie_title: str
    total_recommendations: int
    recommendations: List[RecommendationItem]


class RatingCreate(BaseModel):
    rating: float = Field(..., ge=1.0, le=10.0, description="Star rating from 1.0 to 10.0")
    review_text: Optional[str] = Field(None, max_length=2000)
    contains_spoilers: bool = False
    author_name: str = Field(..., min_length=2, max_length=100, description="Name or critic handle of the reviewer")


class ReviewOut(BaseModel):
    id: int
    movie_id: int
    rating: float
    review_text: Optional[str] = None
    contains_spoilers: bool = False
    author_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class WatchlistToggleRequest(BaseModel):
    movie_id: int


class WatchlistResponse(BaseModel):
    movie_id: int
    in_watchlist: bool
    watchlist_count: int
    message: str


class AnalyticsSummary(BaseModel):
    total_movies: int
    average_rating: float
    total_box_office: int
    top_grossing_movie: Optional[str] = None
    top_rated_movie: Optional[str] = None
    years_span: str


class AnalyticsTrends(BaseModel):
    decades: List[dict]
    top_revenue: List[dict]
    genres_distribution: List[dict]
    languages_share: List[dict]


class ReindexResponse(BaseModel):
    status: str
    total_indexed: int
    elapsed_seconds: float
    message: str
