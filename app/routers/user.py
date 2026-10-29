import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Movie, ReviewRating, Watchlist
from app.posters import format_revenue, get_backdrop_url, get_poster_url
from app.schemas import (
    MovieCardOut,
    RatingCreate,
    ReviewOut,
    WatchlistResponse,
    WatchlistToggleRequest,
)

log = logging.getLogger("cinematch.user")
router = APIRouter(prefix="/api", tags=["user engagement"])


@router.post("/movies/{movie_id}/rating", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def submit_rating_and_review(
    movie_id: int,
    body: RatingCreate,
    db: Session = Depends(get_db),
):
    """
    Submit interactive user rating (1-10) and written review text with spoiler flag.
    Also slightly retunes the movie's community vote_average if relevant.
    """
    movie = db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found")

    # Always create a new review record so every reviewer's review is preserved
    clean_author = (body.author_name or "").strip()
    if not clean_author or clean_author.lower() in ("anonymous", "anonymous cinephile"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A reviewer name or critic handle is required to post a review."
        )

    review = ReviewRating(
        movie_id=movie_id,
        rating=round(body.rating, 1),
        review_text=body.review_text.strip() if body.review_text else None,
        contains_spoilers=body.contains_spoilers,
        author_name=clean_author,
    )
    db.add(review)

    # Retune movie community rating slightly based on user input
    current_avg = movie.vote_average or body.rating
    current_count = movie.vote_count or 1
    new_count = current_count + 1
    new_avg = ((current_avg * current_count) + body.rating) / new_count
    movie.vote_average = round(new_avg, 2)
    movie.vote_count = new_count

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        err_msg = str(e).lower()
        if "unique constraint" in err_msg or "duplicate key" in err_msg or "reviews_pkey" in err_msg:
            try:
                from sqlalchemy import text
                db.execute(text("SELECT setval(pg_get_serial_sequence('reviews', 'id'), COALESCE((SELECT MAX(id) FROM reviews), 1));"))
                db.commit()
                if not existing_review:
                    db.add(review)
                    db.commit()
            except Exception as e2:
                log.exception("Sequence recovery failed: %s", e2)
                raise HTTPException(status_code=500, detail="Error saving review")
        else:
            log.exception("Submit review error: %s", e)
            raise HTTPException(status_code=500, detail="Error saving review")

    # Interoperability: Also record interaction in Supabase for partner analytics
    try:
        from sqlalchemy import text
        db.execute(text("""
            INSERT INTO interactions (user_id, movie_id, interaction_type, slot, rating, active, created_at, updated_at)
            VALUES (:u, :m, 'rating', 'rating', :r, true, NOW(), NOW())
            ON CONFLICT (user_id, movie_id, slot) DO UPDATE
            SET rating = EXCLUDED.rating, updated_at = NOW();
        """), {"u": "cinephile_guest", "m": movie_id, "r": round(body.rating, 1)})
        db.commit()
    except Exception:
        pass

    db.refresh(review)
    return review


@router.get("/movies/{movie_id}/reviews", response_model=List[ReviewOut])
def get_movie_reviews(movie_id: int, db: Session = Depends(get_db)):
    """Retrieve all submitted user reviews and ratings for a movie."""
    reviews = db.scalars(
        select(ReviewRating).where(ReviewRating.movie_id == movie_id).order_by(ReviewRating.created_at.desc())
    ).all()
    return reviews


@router.get("/watchlist", response_model=List[MovieCardOut])
def get_watchlist(db: Session = Depends(get_db)):
    """Retrieve all user saved movies currently stored in the watchlist."""
    watchlist_records = db.scalars(
        select(Watchlist).order_by(Watchlist.created_at.desc())
    ).all()

    items = []
    for entry in watchlist_records:
        m = entry.movie
        if m:
            cast_names = [c["name"] for c in (m.cast_members or [])[:4] if isinstance(c, dict) and c.get("name")]
            items.append(
                MovieCardOut(
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
                    is_in_watchlist=True,
                )
            )
    return items


@router.post("/watchlist", response_model=WatchlistResponse)
def toggle_watchlist(body: WatchlistToggleRequest, db: Session = Depends(get_db)):
    """Add or remove a movie from user's persistent watchlist."""
    movie = db.get(Movie, body.movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {body.movie_id} not found")

    existing = db.scalars(
        select(Watchlist).where(Watchlist.movie_id == body.movie_id)
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        in_watchlist = False
        message = f"Removed '{movie.title}' from your watchlist."
    else:
        new_entry = Watchlist(movie_id=body.movie_id)
        db.add(new_entry)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            err_msg = str(e).lower()
            if "unique constraint" in err_msg or "duplicate key" in err_msg or "watchlist_pkey" in err_msg:
                try:
                    from sqlalchemy import text
                    db.execute(text("SELECT setval(pg_get_serial_sequence('watchlist', 'id'), COALESCE((SELECT MAX(id) FROM watchlist), 1));"))
                    db.commit()
                    db.add(new_entry)
                    db.commit()
                except Exception as e2:
                    log.exception("Watchlist sequence recovery failed: %s", e2)
                    raise HTTPException(status_code=500, detail="Error updating watchlist")
            else:
                raise
        in_watchlist = True
        message = f"Saved '{movie.title}' to your watchlist."

    total_count = db.scalar(select(func.count(Watchlist.id))) or 0
    return WatchlistResponse(
        movie_id=body.movie_id,
        in_watchlist=in_watchlist,
        watchlist_count=total_count,
        message=message,
    )


@router.delete("/watchlist/{movie_id}", response_model=WatchlistResponse)
def remove_from_watchlist(movie_id: int, db: Session = Depends(get_db)):
    """Explicitly remove a movie from the watchlist."""
    existing = db.scalars(
        select(Watchlist).where(Watchlist.movie_id == movie_id)
    ).first()

    if existing:
        db.delete(existing)
        db.commit()

    total_count = db.scalar(select(func.count(Watchlist.id))) or 0
    return WatchlistResponse(
        movie_id=movie_id,
        in_watchlist=False,
        watchlist_count=total_count,
        message="Movie removed from watchlist",
    )
