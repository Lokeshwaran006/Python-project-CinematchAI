import logging
import math
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import cast, desc, func, or_, select, String
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Movie, Watchlist
from app.posters import (
    calculate_rt_score,
    format_revenue,
    get_backdrop_url,
    get_poster_url,
)
from app.recommender import recommender
from app.schemas import (
    MovieCardOut,
    MovieCreate,
    MovieOut,
    MovieUpdate,
    PaginatedMovies,
)

log = logging.getLogger("cinematch.movies")
router = APIRouter(prefix="/api/movies", tags=["movies"])


LANGUAGE_MAP = {
    "english": "en",
    "en": "en",
    "spanish": "es",
    "es": "es",
    "hindi": "hi",
    "hi": "hi",
    "french": "fr",
    "fr": "fr",
    "japanese": "ja",
    "ja": "ja",
    "german": "de",
    "de": "de",
    "italian": "it",
    "it": "it",
    "korean": "ko",
    "ko": "ko",
    "chinese": "zh",
    "mandarin": "zh",
    "zh": "zh",
    "cn": "cn",
    "cantonese": "cn",
    "russian": "ru",
    "ru": "ru",
    "portuguese": "pt",
    "pt": "pt",
    "tamil": "ta",
    "ta": "ta",
    "telugu": "te",
    "te": "te",
}


def build_movie_card(m: Movie, in_watchlist: bool = False) -> MovieCardOut:
    """Helper to convert Movie ORM object to MovieCardOut schema."""
    cast_names = [c["name"] for c in (m.cast_members or [])[:4] if isinstance(c, dict) and c.get("name")]
    return MovieCardOut(
        id=m.id,
        title=m.title,
        year=m.year,
        release_date=m.release_date.isoformat() if m.release_date else None,
        vote_average=m.vote_average,
        vote_count=m.vote_count or 0,
        genres=m.genres or [],
        original_language=m.original_language or "en",
        revenue=m.revenue,
        revenue_display=format_revenue(m.revenue),
        poster_url=get_poster_url(m),
        backdrop_url=get_backdrop_url(m),
        director=m.director,
        cast=cast_names,
        is_in_watchlist=in_watchlist,
    )


@router.get("", response_model=PaginatedMovies)
def get_movies(
    search: Optional[str] = Query(None, description="Case-insensitive title, director or actor search"),
    genres: Optional[List[str]] = Query(None, description="Multi-select genres"),
    year_min: Optional[int] = Query(None, ge=1880, le=2030),
    year_max: Optional[int] = Query(None, ge=1880, le=2030),
    min_rating: Optional[float] = Query(None, ge=0.0, le=10.0),
    language: Optional[str] = Query(None),
    sort_by: str = Query("Highest Rated", description="Highest Rated, Highest Revenue, Release Date, Most Relevant"),
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Movie Catalog and Multi-Attribute Search API matching the exact filters displayed in Page 3.
    """
    stmt = select(Movie)

    # Search filter: Title, Director, or Cast
    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Movie.title).like(term),
                func.lower(Movie.director).like(term),
                func.lower(Movie.overview).like(term),
            )
        )

    # Genre multi-select filter (handle both list and comma-separated string)
    parsed_genres = []
    if genres:
        for g in genres:
            if "," in g:
                parsed_genres.extend([item.strip() for item in g.split(",") if item.strip()])
            elif g.strip():
                parsed_genres.append(g.strip())

    if parsed_genres:
        genre_clauses = [cast(Movie.genres, String).ilike(f"%{genre}%") for genre in parsed_genres]
        stmt = stmt.where(or_(*genre_clauses))

    # Year range filters
    if year_min is not None:
        stmt = stmt.where(Movie.year >= year_min)
    if year_max is not None:
        stmt = stmt.where(Movie.year <= year_max)

    # Minimum Rating threshold
    if min_rating is not None and min_rating > 0.0:
        stmt = stmt.where(Movie.vote_average >= min_rating)

    # Language filter (supports full names like 'English', 'Spanish' and ISO codes like 'en', 'es')
    if language and language.strip() and language.lower() not in ("all", "all languages", "any"):
        lang_clean = language.strip().lower()
        lang_code = LANGUAGE_MAP.get(lang_clean, lang_clean)
        stmt = stmt.where(
            or_(
                func.lower(Movie.original_language) == lang_code,
                func.lower(Movie.original_language) == lang_clean
            )
        )

    # Sorting
    sort_norm = sort_by.strip().lower()
    if "revenue" in sort_norm:
        stmt = stmt.order_by(Movie.revenue.desc().nullslast(), Movie.vote_average.desc().nullslast())
    elif "date" in sort_norm or "release" in sort_norm:
        stmt = stmt.order_by(Movie.release_date.desc().nullslast(), Movie.popularity.desc().nullslast())
    elif "relevant" in sort_norm or "popularity" in sort_norm:
        stmt = stmt.order_by(Movie.popularity.desc().nullslast(), Movie.vote_average.desc().nullslast())
    else:  # Default: Highest Rated
        stmt = stmt.order_by(Movie.vote_average.desc().nullslast(), Movie.vote_count.desc())

    # Count total matching
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.scalar(count_stmt) or 0

    # Pagination
    offset = (page - 1) * limit
    paginated_stmt = stmt.offset(offset).limit(limit)
    movies = db.scalars(paginated_stmt).all()

    # User watchlist items
    watchlist_ids = set(db.scalars(select(Watchlist.movie_id)).all())

    items = [build_movie_card(m, in_watchlist=(m.id in watchlist_ids)) for m in movies]
    pages = math.ceil(total / limit) if total > 0 else 1

    return PaginatedMovies(
        total=total,
        page=page,
        limit=limit,
        pages=pages,
        items=items,
    )


@router.get("/{movie_id}", response_model=MovieOut)
def get_movie_detail(movie_id: int, db: Session = Depends(get_db)):
    """Retrieve full movie record with Rotten Tomatoes score, poster URLs, and watchlist state."""
    movie = db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found")

    is_saved = db.scalar(select(func.count(Watchlist.id)).where(Watchlist.movie_id == movie_id)) > 0
    rt_score = calculate_rt_score(movie.vote_average, movie.vote_count)

    return MovieOut(
        id=movie.id,
        title=movie.title,
        original_title=movie.original_title,
        overview=movie.overview,
        tagline=movie.tagline,
        status=movie.status,
        release_date=movie.release_date,
        year=movie.year,
        vote_average=movie.vote_average,
        vote_count=movie.vote_count,
        popularity=movie.popularity,
        budget=movie.budget,
        revenue=movie.revenue,
        runtime=movie.runtime,
        original_language=movie.original_language,
        genres=movie.genres or [],
        keywords=movie.keywords or [],
        production_companies=movie.production_companies or [],
        production_countries=movie.production_countries or [],
        director=movie.director,
        cast_members=movie.cast_members or [],
        crew_members=movie.crew_members or [],
        poster_path=movie.poster_path,
        backdrop_path=movie.backdrop_path,
        created_at=movie.created_at,
        updated_at=movie.updated_at,
        last_edited_by=movie.last_edited_by,
        poster_url=get_poster_url(movie),
        backdrop_url=get_backdrop_url(movie),
        rotten_tomatoes_pct=rt_score,
        revenue_display=format_revenue(movie.revenue),
        budget_display=format_revenue(movie.budget),
        is_in_watchlist=is_saved,
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=MovieOut)
def create_movie(body: MovieCreate, db: Session = Depends(get_db)):
    """
    Partner CRUD: Add a new movie record with Pydantic validation.
    Triggers automated re-indexing pipeline so ML vectors update in real-time.
    """
    if db.get(Movie, body.id) is not None:
        raise HTTPException(status_code=409, detail=f"Movie with ID {body.id} already exists")

    data = body.model_dump()
    data["year"] = body.release_date.year if body.release_date else None
    data["last_edited_by"] = "Partner API Mutation"

    movie = Movie(**data)
    db.add(movie)
    db.commit()
    db.refresh(movie)

    # Trigger real-time re-indexing
    try:
        recommender.reindex(db)
        log.info("Re-indexer triggered after POST /api/movies for movie ID %d", movie.id)
    except Exception as e:
        log.warning("Re-index post-create warning: %s", e)

    return get_movie_detail(movie.id, db)


@router.put("/{movie_id}", response_model=MovieOut)
def update_movie(movie_id: int, body: MovieUpdate, db: Session = Depends(get_db)):
    """
    Partner CRUD: Update an existing movie's ratings, revenue, cast, or metadata.
    Triggers automated re-indexing pipeline.
    """
    movie = db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found")

    changes = body.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="No updated fields provided")

    if "release_date" in changes and changes["release_date"]:
        movie.year = changes["release_date"].year

    for field, value in changes.items():
        setattr(movie, field, value)

    movie.last_edited_by = "Partner API Mutation"
    db.commit()
    db.refresh(movie)

    # Trigger real-time re-indexing
    try:
        recommender.reindex(db)
        log.info("Re-indexer triggered after PUT /api/movies for movie ID %d", movie.id)
    except Exception as e:
        log.warning("Re-index post-update warning: %s", e)

    return get_movie_detail(movie.id, db)


@router.delete("/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    """
    Partner CRUD: Remove a movie from the catalog.
    Triggers automated re-indexing pipeline.
    """
    movie = db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found")

    db.delete(movie)
    db.commit()

    # Trigger real-time re-indexing
    try:
        recommender.reindex(db)
        log.info("Re-indexer triggered after DELETE /api/movies for movie ID %d", movie_id)
    except Exception as e:
        log.warning("Re-index post-delete warning: %s", e)

    return {"status": "deleted", "id": movie_id, "message": f"Movie {movie_id} removed successfully"}
