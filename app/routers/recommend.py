import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Movie
from app.recommender import recommender
from app.schemas import RecommendationItem, RecommendationResponse

log = logging.getLogger("cinematch.recommend")
router = APIRouter(prefix="/api/recommend", tags=["recommendations"])


@router.get("/{movie_id}", response_model=RecommendationResponse)
def get_recommendations_for_movie(
    movie_id: int,
    limit: int = Query(8, ge=1, le=24, description="Number of recommendations to return"),
    db: Session = Depends(get_db),
):
    """
    Scikit-Learn Content-Based Recommendation Engine:
    - Generates similarity vectors from TF-IDF feature matrix.
    - Computes cosine similarity scores on demand.
    - Returns top 8 similar titles with match percentages (e.g., '98% Match')
      and algorithmic rationale tags.
    """
    movie = db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with ID {movie_id} not found")

    query_info, recs = recommender.get_recommendations(movie_id, limit=limit)
    if not recs and (recommender.df.empty or recommender.tfidf_matrix is None):
        recommender.reindex(db)
        query_info, recs = recommender.get_recommendations(movie_id, limit=limit)

    items = [
        RecommendationItem(
            id=r["id"],
            title=r["title"],
            year=r["year"],
            vote_average=r["vote_average"],
            genres=r["genres"],
            director=r["director"],
            poster_url=r["poster_url"],
            match_percentage=r["match_percentage"],
            rationale_tags=r["rationale_tags"],
            primary_reason=r["primary_reason"],
        )
        for r in recs
    ]

    return RecommendationResponse(
        query_movie_id=movie_id,
        query_movie_title=movie.title,
        total_recommendations=len(items),
        recommendations=items,
    )
