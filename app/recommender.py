import json
import logging
import re
import threading
import time
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import DB_FILE
from app.database import SessionLocal
from app.models import Movie
from app.posters import get_backdrop_url, get_poster_url

log = logging.getLogger("cinematch.recommender")


def clean_token(text: str) -> str:
    """Normalize names and phrases into single continuous tokens, e.g. 'Christopher Nolan' -> 'christophernolan'."""
    return re.sub(r"[^a-zA-Z0-9]", "", str(text)).lower()


class ContentRecommender:
    """
    Scikit-Learn Content-Based Recommendation Engine with TF-IDF Vectorization
    and Cosine Similarity scoring. Supports dynamic real-time re-indexing.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self.df: pd.DataFrame = pd.DataFrame()
        self.tfidf_matrix = None
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.id_to_idx: Dict[int, int] = {}
        self.idx_to_id: Dict[int, int] = {}
        self.last_indexed_at: Optional[float] = None

    def _build_soup(self, row: pd.Series) -> str:
        """Create a heavily-weighted metadata soup combining overview, genres, cast, director, and keywords."""
        parts = []

        # Overview
        overview = str(row.get("overview") or "").strip()
        if overview:
            parts.append(overview)

        # Genres (weighted x2)
        genres = row.get("genres") or []
        if isinstance(genres, str):
            try:
                genres = json.loads(genres)
            except Exception:
                genres = []
        if isinstance(genres, list):
            genre_tokens = " ".join([clean_token(g) for g in genres if g])
            parts.extend([genre_tokens, genre_tokens])

        # Director (weighted x3 for strong signature)
        director = row.get("director")
        if director and str(director).strip():
            dir_token = clean_token(director)
            parts.extend([dir_token, dir_token, dir_token])

        # Cast (top 4, weighted x2)
        cast_members = row.get("cast_members") or []
        if isinstance(cast_members, str):
            try:
                cast_members = json.loads(cast_members)
            except Exception:
                cast_members = []
        if isinstance(cast_members, list):
            cast_names = [clean_token(c.get("name")) for c in cast_members[:4] if isinstance(c, dict) and c.get("name")]
            cast_tokens = " ".join(cast_names)
            parts.extend([cast_tokens, cast_tokens])

        # Keywords (top 8)
        keywords = row.get("keywords") or []
        if isinstance(keywords, str):
            try:
                keywords = json.loads(keywords)
            except Exception:
                keywords = []
        if isinstance(keywords, list):
            kw_tokens = " ".join([clean_token(k) for k in keywords[:8] if k])
            parts.append(kw_tokens)

        return " ".join(parts)

    def reindex(self, session: Optional[Session] = None) -> dict:
        """Rebuild the TF-IDF vector matrix dynamically in background memory."""
        t0 = time.time()
        data = []

        # Fast-path: If local cinematch.db exists, read from local SQLite (sub-100ms)
        # to prevent downloading 4,808 large rows over international network on startup.
        if DB_FILE.exists():
            try:
                from sqlalchemy import create_engine
                from sqlalchemy.orm import sessionmaker
                local_eng = create_engine(f"sqlite:///{DB_FILE.as_posix()}", connect_args={"check_same_thread": False})
                with sessionmaker(bind=local_eng)() as local_s:
                    movies = local_s.scalars(select(Movie).order_by(Movie.id)).all()
                    for m in movies:
                        data.append({
                            "id": int(m.id),
                            "title": m.title,
                            "overview": m.overview or "",
                            "genres": m.genres or [],
                            "keywords": m.keywords or [],
                            "director": m.director or "",
                            "cast_members": m.cast_members or [],
                            "vote_average": m.vote_average or 0.0,
                            "vote_count": m.vote_count or 0,
                            "year": m.year,
                            "poster_path": m.poster_path,
                            "backdrop_path": m.backdrop_path,
                        })
            except Exception as e:
                log.warning("Local SQLite quick-read note: %s", e)
                data = []

        # Cloud fallback: query lightweight columns if local DB is not available
        if not data:
            close_session = False
            if session is None:
                session = SessionLocal()
                close_session = True

            try:
                cols = [
                    Movie.id, Movie.title, Movie.overview, Movie.genres,
                    Movie.keywords, Movie.director, Movie.cast_members,
                    Movie.vote_average, Movie.vote_count, Movie.year,
                    Movie.poster_path, Movie.backdrop_path
                ]
                rows = session.execute(select(*cols).order_by(Movie.id)).all()
                for r in rows:
                    data.append({
                        "id": int(r[0]),
                        "title": r[1],
                        "overview": r[2] or "",
                        "genres": r[3] or [],
                        "keywords": r[4] or [],
                        "director": r[5] or "",
                        "cast_members": r[6] or [],
                        "vote_average": r[7] or 0.0,
                        "vote_count": r[8] or 0,
                        "year": r[9],
                        "poster_path": r[10],
                        "backdrop_path": r[11],
                    })
            finally:
                if close_session:
                    session.close()

        if not data:
            log.warning("Re-index called but no movies found in database.")
            return {"status": "empty", "total_indexed": 0, "elapsed_seconds": 0.0}

        df = pd.DataFrame(data)
        df["soup"] = df.apply(self._build_soup, axis=1)

        # Fit TF-IDF Vectorizer
        vectorizer = TfidfVectorizer(stop_words="english", max_features=10000)
        tfidf_matrix = vectorizer.fit_transform(df["soup"])

        id_to_idx = {int(row["id"]): i for i, row in enumerate(data)}
        idx_to_id = {i: int(row["id"]) for i, row in enumerate(data)}

        elapsed = round(time.time() - t0, 3)
        with self._lock:
            self.df = df
            self.vectorizer = vectorizer
            self.tfidf_matrix = tfidf_matrix
            self.id_to_idx = id_to_idx
            self.idx_to_id = idx_to_id
            self.last_indexed_at = time.time()

        log.info("TF-IDF matrix rebuilt with %d movies in %.3fs.", len(df), elapsed)
        return {
            "status": "success",
            "total_indexed": len(df),
            "elapsed_seconds": elapsed,
            "message": f"Successfully re-indexed {len(df)} movies in {elapsed}s",
        }

    def get_recommendations(self, movie_id: int, limit: int = 8) -> Tuple[Optional[dict], List[dict]]:
        """
        Return the query movie details and top `limit` similar movies with match percentage
        and algorithmic rationale tags.
        """
        movie_id = int(movie_id)
        with self._lock:
            if self.df.empty or self.tfidf_matrix is None:
                self.reindex()

            if movie_id not in self.id_to_idx:
                return None, []

            idx = self.id_to_idx[movie_id]
            query_row = self.df.iloc[idx]
            query_vector = self.tfidf_matrix[idx:idx + 1]

            # Fast cosine similarity via linear_kernel
            sim_scores = linear_kernel(query_vector, self.tfidf_matrix).flatten()

        # Sort indices descending
        sorted_indices = sim_scores.argsort()[::-1]

        recommendations = []
        for sim_idx in sorted_indices:
            if sim_idx == idx:
                continue  # Skip query movie itself

            sim_row = self.df.iloc[sim_idx]
            raw_sim = float(sim_scores[sim_idx])

            # Convert cosine similarity into a realistic taste match percentage (e.g. 88% - 98%)
            # High raw cosine similarity in TF-IDF (0.3 - 0.7) corresponds to 90%+ match
            scaled_pct = int(min(98, max(75, 78 + (raw_sim * 42))))

            # Determine algorithmic rationale tags
            rationale_tags = []
            q_genres = set(query_row["genres"] or [])
            s_genres = set(sim_row["genres"] or [])
            shared_genres = list(q_genres.intersection(s_genres))

            if shared_genres:
                rationale_tags.append(f"Matches preference for {shared_genres[0]}")

            if query_row["director"] and sim_row["director"] and query_row["director"] == sim_row["director"]:
                rationale_tags.append(f"{query_row['director']}")

            if sim_row["vote_average"] and sim_row["vote_average"] >= 7.5:
                rationale_tags.append(f"High IMDb Score · {sim_row['vote_average']:.1f}/10")

            # Check shared cast
            q_cast = {c.get("name") for c in query_row["cast_members"] if isinstance(c, dict) and c.get("name")}
            s_cast = {c.get("name") for c in sim_row["cast_members"] if isinstance(c, dict) and c.get("name")}
            shared_cast = list(q_cast.intersection(s_cast))
            if shared_cast and len(rationale_tags) < 3:
                rationale_tags.append(f"Starring {shared_cast[0]}")

            # Fallbacks if needed
            if len(rationale_tags) == 0:
                rationale_tags.append("Similar Narrative Themes")
            if len(rationale_tags) == 1 and shared_genres:
                rationale_tags.append(f"Curated {shared_genres[0]} Classic")

            primary_reason = f"Based on strong narrative and genre alignment with {query_row['title']}."
            if shared_genres and query_row["director"] and query_row["director"] == sim_row["director"]:
                primary_reason = f"Shared {shared_genres[0]} universe and director {query_row['director']}'s signature vision."

            recommendations.append({
                "id": int(sim_row["id"]),
                "title": str(sim_row["title"]),
                "year": int(sim_row["year"]) if sim_row["year"] and not pd.isna(sim_row["year"]) else None,
                "vote_average": float(sim_row["vote_average"]) if sim_row["vote_average"] else None,
                "genres": sim_row["genres"] or [],
                "director": sim_row["director"] or None,
                "poster_url": get_poster_url(sim_row.to_dict()),
                "match_percentage": scaled_pct,
                "rationale_tags": rationale_tags[:3],
                "primary_reason": primary_reason,
            })

            if len(recommendations) >= limit:
                break

        query_info = {
            "id": int(query_row["id"]),
            "title": str(query_row["title"]),
            "year": int(query_row["year"]) if query_row["year"] and not pd.isna(query_row["year"]) else None,
            "genres": query_row["genres"] or [],
            "director": query_row["director"] or None,
            "poster_url": get_poster_url(query_row.to_dict()),
            "backdrop_url": get_backdrop_url(query_row.to_dict()),
        }

        return query_info, recommendations


# Global singleton instance
recommender = ContentRecommender()
