import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select

from app.config import (
    APP_DESCRIPTION,
    APP_DIR,
    APP_NAME,
    CORS_ORIGINS,
    DB_FILE,
)
from app.database import SessionLocal, init_db
from app.ingest import ingest_data
from app.models import Movie
from app.posters import generate_svg_poster
from app.recommender import recommender
from app.routers import analytics, movies, recommend, reindex, user, views

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("cinematch.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup lifecycle:
    1. Initialize SQLite schema in cinematch.db (shared database).
    2. Check if movies table is seeded; if not, run automatic ingestion from datasets/.
    3. Rebuild Scikit-Learn TF-IDF vector matrix in memory for sub-millisecond recommendations.
    """
    log.info("Starting up %s...", APP_NAME)
    init_db()

    with SessionLocal() as db:
        movie_count = db.scalar(select(func.count(Movie.id))) or 0
        if movie_count == 0:
            log.info("Database is empty. Initiating automatic TMDB dataset ingestion...")
            try:
                result = ingest_data()
                log.info("Auto-ingestion completed: %s", result)
            except Exception as e:
                log.exception("Automatic dataset ingestion failed: %s", e)
        else:
            log.info("Database already seeded with %d movies in %s", movie_count, DB_FILE)

        # Build in-memory TF-IDF index
        try:
            log.info("Building recommendation engine matrix...")
            rec_result = recommender.reindex(db)
            log.info("Recommender initialized: %s", rec_result)
        except Exception as e:
            log.exception("Failed to initialize recommender: %s", e)

    yield
    log.info("Shutting down %s.", APP_NAME)


app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Static Files
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")

# Dynamic SVG poster route for resilient offline rendering
@app.get("/api/poster/{movie_id}.svg", include_in_schema=False)
def dynamic_poster_svg(movie_id: int):
    with SessionLocal() as db:
        movie = db.get(Movie, movie_id)
        title = movie.title if movie else f"Movie {movie_id}"
        year = movie.year if movie else None
        genre = movie.genres[0] if (movie and movie.genres) else "Cinema"
        svg_data = generate_svg_poster(title, year, genre)
        # Strip data URL prefix if returning raw SVG
        prefix = "data:image/svg+xml;charset=utf-8,"
        svg_content = svg_data[len(prefix):] if svg_data.startswith(prefix) else svg_data
        import urllib.parse
        raw_svg = urllib.parse.unquote(svg_content)
        return Response(content=raw_svg, media_type="image/svg+xml")

# Include Routers
app.include_router(views.router)
app.include_router(movies.router)
app.include_router(recommend.router)
app.include_router(analytics.router)
app.include_router(user.router)
app.include_router(reindex.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
