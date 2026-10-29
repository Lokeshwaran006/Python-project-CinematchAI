import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.recommender import recommender
from app.schemas import ReindexResponse

log = logging.getLogger("cinematch.reindex")
router = APIRouter(prefix="/api/reindex", tags=["pipeline"])


@router.post("", response_model=ReindexResponse)
def trigger_reindex(db: Session = Depends(get_db)):
    """
    Manually trigger the Scikit-Learn TF-IDF vectorization and recommendation pipeline.
    Dynamically recalculates all feature matrices in background memory without server restart.
    """
    log.info("Manual re-index triggered via POST /api/reindex")
    result = recommender.reindex(db)
    return ReindexResponse(
        status=result["status"],
        total_indexed=result["total_indexed"],
        elapsed_seconds=result["elapsed_seconds"],
        message=result["message"],
    )
