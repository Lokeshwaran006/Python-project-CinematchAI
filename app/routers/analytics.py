import logging
from collections import Counter
from typing import Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Movie
from app.posters import format_revenue
from app.schemas import AnalyticsSummary, AnalyticsTrends

log = logging.getLogger("cinematch.analytics")
router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_analytics_summary(db: Session = Depends(get_db)):
    """Summary metrics consumed by partner's visualization and intelligence components."""
    total = db.scalar(select(func.count(Movie.id))) or 0
    avg_rating = db.scalar(select(func.avg(Movie.vote_average))) or 0.0
    total_rev = db.scalar(select(func.sum(Movie.revenue))) or 0

    top_grossing = db.scalars(
        select(Movie).where(Movie.revenue.isnot(None)).order_by(Movie.revenue.desc()).limit(1)
    ).first()

    top_rated = db.scalars(
        select(Movie).where(Movie.vote_count >= 500).order_by(Movie.vote_average.desc()).limit(1)
    ).first()

    min_year = db.scalar(select(func.min(Movie.year))) or 1920
    max_year = db.scalar(select(func.max(Movie.year))) or 2026

    return AnalyticsSummary(
        total_movies=total,
        average_rating=round(float(avg_rating), 2),
        total_box_office=int(total_rev),
        top_grossing_movie=top_grossing.title if top_grossing else None,
        top_rated_movie=top_rated.title if top_rated else None,
        years_span=f"{min_year} - {max_year}",
    )


@router.get("/trends", response_model=AnalyticsTrends)
def get_analytics_trends(db: Session = Depends(get_db)):
    """
    Dedicated analytical trends API aggregating:
    - Release count by decade
    - Top 10 revenue leaders
    - Genre distribution counts
    - Language share
    """
    movies = db.scalars(select(Movie)).all()

    # 1. Decade breakdown
    decades_counter: Counter = Counter()
    for m in movies:
        if m.year:
            dec = (m.year // 10) * 10
            decades_counter[f"{dec}s"] += 1

    decades = [
        {"decade": dec, "count": count}
        for dec, count in sorted(decades_counter.items(), key=lambda x: x[0])
    ]

    # 2. Top 10 revenue leaders
    top_rev_movies = db.scalars(
        select(Movie).where(Movie.revenue.isnot(None)).order_by(Movie.revenue.desc()).limit(10)
    ).all()

    top_revenue = [
        {
            "id": m.id,
            "title": m.title,
            "revenue": m.revenue,
            "revenue_formatted": format_revenue(m.revenue),
            "year": m.year,
            "vote_average": m.vote_average,
        }
        for m in top_rev_movies
    ]

    # 3. Genre distribution counts
    genre_counter: Counter = Counter()
    for m in movies:
        for g in (m.genres or []):
            if g:
                genre_counter[g] += 1

    genres_distribution = [
        {"genre": genre, "count": count}
        for genre, count in genre_counter.most_common(20)
    ]

    # 4. Language share
    lang_counter: Counter = Counter()
    for m in movies:
        if m.original_language:
            lang_counter[m.original_language.lower()] += 1

    total_movies = len(movies) or 1
    languages_share = [
        {
            "language": lang,
            "count": count,
            "percentage": round((count / total_movies) * 100, 1),
        }
        for lang, count in lang_counter.most_common(10)
    ]

    return AnalyticsTrends(
        decades=decades,
        top_revenue=top_revenue,
        genres_distribution=genres_distribution,
        languages_share=languages_share,
    )


@router.get("/genres")
def get_genres_stats(db: Session = Depends(get_db)):
    """Genre statistics for partner visualizations."""
    movies = db.scalars(select(Movie)).all()
    genre_counts: Counter = Counter()
    genre_ratings: Dict[str, list] = {}

    for m in movies:
        for g in (m.genres or []):
            if g:
                genre_counts[g] += 1
                if m.vote_average:
                    genre_ratings.setdefault(g, []).append(m.vote_average)

    result = []
    for g, count in genre_counts.most_common():
        ratings = genre_ratings.get(g, [])
        avg = round(sum(ratings) / len(ratings), 2) if ratings else None
        result.append({"genre": g, "movie_count": count, "average_rating": avg})

    return {"genres": result}


@router.get("/ratings")
def get_ratings_stats(db: Session = Depends(get_db)):
    """Rating distribution buckets (1 to 10)."""
    movies = db.scalars(select(Movie.vote_average).where(Movie.vote_average.isnot(None))).all()
    buckets: Counter = Counter()
    for r in movies:
        b = int(r)
        buckets[f"{b}-{b+1}"] += 1

    return {
        "buckets": [{"range": k, "count": buckets[k]} for k in sorted(buckets.keys())],
        "total_rated": len(movies),
    }
