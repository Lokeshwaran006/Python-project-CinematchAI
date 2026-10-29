from datetime import date, datetime, timezone
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base

JsonType = JSON().with_variant(JSONB(), "postgresql")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Movie(Base):
    """
    Shared movie table between CineMatch AI and Movie Analytics Dashboard.
    `id` is the TMDB movie id and serves as the single source of truth.
    """
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(String(300), nullable=False, index=True)
    original_title = Column(String(300), nullable=True)
    overview = Column(Text, nullable=True)
    tagline = Column(Text, nullable=True)
    status = Column(String(50), nullable=True, default="Released")
    release_date = Column(Date, nullable=True, index=True)
    year = Column(Integer, nullable=True, index=True)
    vote_average = Column(Float, nullable=True, index=True)
    vote_count = Column(Integer, default=0)
    popularity = Column(Float, nullable=True, index=True)
    budget = Column(BigInteger, nullable=True)
    revenue = Column(BigInteger, nullable=True)
    runtime = Column(Float, nullable=True)
    original_language = Column(String(10), nullable=True, index=True)
    genres = Column(JsonType, default=list)  # ["Action", "Sci-Fi"]
    keywords = Column(JsonType, default=list)  # ["space", "dune"]
    production_companies = Column(JsonType, default=list)
    production_countries = Column(JsonType, default=list)
    director = Column(String(200), nullable=True, index=True)
    cast_members = Column(JsonType, default=list)  # [{"name": "...", "character": "..."}]
    crew_members = Column(JsonType, default=list)  # [{"name": "...", "job": "..."}]
    poster_path = Column(String(500), nullable=True)
    backdrop_path = Column(String(500), nullable=True)
    poster_checked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    last_edited_by = Column(String(60), nullable=True)

    reviews = relationship("ReviewRating", back_populates="movie", cascade="all, delete-orphan")
    watchlist_entry = relationship("Watchlist", back_populates="movie", uselist=False, cascade="all, delete-orphan")


class ReviewRating(Base):
    """User reviews, ratings (1-10), and spoiler feedback."""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Float, nullable=False)  # 1.0 to 10.0
    review_text = Column(Text, nullable=True)
    contains_spoilers = Column(Boolean, default=False)
    author_name = Column(String(100), default="Anonymous Cinephile")
    created_at = Column(DateTime(timezone=True), default=utcnow)

    movie = relationship("Movie", back_populates="reviews")


class Watchlist(Base):
    """User saved movies for quick watchlist access."""
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    movie = relationship("Movie", back_populates="watchlist_entry")


class Editor(Base):
    """Editor accounts for authenticated data mutations (POST, PUT, DELETE)."""
    __tablename__ = "editors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(60), unique=True, nullable=False, index=True)
    password_hash = Column(String(300), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
