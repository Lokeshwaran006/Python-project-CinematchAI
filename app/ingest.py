import json
import logging
from datetime import date
from pathlib import Path
from typing import Any, List, Optional

import numpy as np
import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import CREDITS_CSV, MOVIES_CSV
from app.database import Base, SessionLocal, engine
from app.models import Movie
from app.posters import CURATED_POSTERS

log = logging.getLogger("cinematch.ingest")


def parse_json_safely(val: Any) -> list:
    """Safely parse JSON string into a list of dicts."""
    if not isinstance(val, str) or not val.strip():
        return []
    try:
        data = json.loads(val)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def extract_names(val: Any, limit: Optional[int] = None) -> List[str]:
    """Extract 'name' attribute from list of dictionaries."""
    items = parse_json_safely(val)
    names = [i["name"] for i in items if isinstance(i, dict) and i.get("name")]
    return names[:limit] if limit else names


def extract_director(crew_val: Any) -> Optional[str]:
    """Find the crew member where job == 'Director'."""
    for person in parse_json_safely(crew_val):
        if isinstance(person, dict) and person.get("job") == "Director" and person.get("name"):
            return person["name"]
    return None


def extract_cast(cast_val: Any, limit: int = 20) -> List[dict]:
    """Extract top cast members with name and character."""
    cast = []
    for p in parse_json_safely(cast_val)[:limit]:
        if isinstance(p, dict) and p.get("name"):
            cast.append({"name": p["name"], "character": p.get("character")})
    return cast


def extract_crew(crew_val: Any, limit: int = 20) -> List[dict]:
    """Extract key crew members."""
    key_jobs = {"Director", "Writer", "Screenplay", "Producer", "Executive Producer",
                "Original Music Composer", "Director of Photography", "Editor"}
    crew = []
    for p in parse_json_safely(crew_val):
        if isinstance(p, dict) and p.get("job") in key_jobs and p.get("name"):
            crew.append({"name": p["name"], "job": p["job"], "department": p.get("department")})
            if len(crew) >= limit:
                break
    return crew


# Mockup-aligned films to ensure 100% pixel & content parity with page 1, 2, and 3
MOCKUP_FEATURED_FILMS = [
    {
        "id": 693134,
        "title": "Dune: Part Two",
        "original_title": "Dune: Part Two",
        "overview": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.",
        "tagline": "Long live the fighters.",
        "status": "Released",
        "release_date": "2024-03-01",
        "year": 2024,
        "vote_average": 8.5,
        "vote_count": 6200,
        "popularity": 420.5,
        "budget": 190000000,
        "revenue": 714400000,
        "runtime": 166.0,
        "original_language": "en",
        "genres": ["Science Fiction", "Adventure"],
        "keywords": ["desert", "spice", "prophecy", "war", "sandworm"],
        "director": "Denis Villeneuve",
        "cast_members": [
            {"name": "Timothée Chalamet", "character": "Paul Atreides"},
            {"name": "Zendaya", "character": "Chani"},
            {"name": "Rebecca Ferguson", "character": "Lady Jessica"},
            {"name": "Javier Bardem", "character": "Stilgar"},
            {"name": "Austin Butler", "character": "Feyd-Rautha Harkonnen"},
        ],
        "crew_members": [{"name": "Denis Villeneuve", "job": "Director", "department": "Directing"}],
        "poster_path": "/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg",
        "backdrop_path": "/xOMo8BRK7PfcJv9JCnx7s520DRq.jpg",
    },
    {
        "id": 335984,
        "title": "Blade Runner 2049",
        "original_title": "Blade Runner 2049",
        "overview": "Thirty years after the events of the first film, a new Blade Runner, LAPD Officer K, unearths a long-buried secret that has the potential to plunge what's left of society into chaos.",
        "tagline": "The key to the future is finally unearthed.",
        "status": "Released",
        "release_date": "2017-10-06",
        "year": 2017,
        "vote_average": 8.0,
        "vote_count": 13500,
        "popularity": 185.0,
        "budget": 150000000,
        "revenue": 259200000,
        "runtime": 164.0,
        "original_language": "en",
        "genres": ["Science Fiction", "Thriller", "Mystery"],
        "keywords": ["dystopia", "replicant", "artificial intelligence", "cyberpunk"],
        "director": "Denis Villeneuve",
        "cast_members": [
            {"name": "Ryan Gosling", "character": "K"},
            {"name": "Harrison Ford", "character": "Rick Deckard"},
            {"name": "Ana de Armas", "character": "Joi"},
            {"name": "Sylvia Hoeks", "character": "Luv"},
            {"name": "Robin Wright", "character": "Lt. Joshi"},
        ],
        "crew_members": [{"name": "Denis Villeneuve", "job": "Director", "department": "Directing"}],
        "poster_path": "/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg",
        "backdrop_path": "/sAtoMqDVhNDQBc3QJL3RF6hlxGq.jpg",
    },
    {
        "id": 329865,
        "title": "Arrival",
        "original_title": "Arrival",
        "overview": "Taking place after alien crafts land around the world, an expert linguist is recruited by the military to determine whether they come in peace or are a threat.",
        "tagline": "Why are they here?",
        "status": "Released",
        "release_date": "2016-11-11",
        "year": 2016,
        "vote_average": 7.9,
        "vote_count": 17200,
        "popularity": 140.0,
        "budget": 47000000,
        "revenue": 203400000,
        "runtime": 116.0,
        "original_language": "en",
        "genres": ["Science Fiction", "Drama", "Mystery"],
        "keywords": ["alien", "linguistics", "first contact", "time", "spacecraft"],
        "director": "Denis Villeneuve",
        "cast_members": [
            {"name": "Amy Adams", "character": "Louise Banks"},
            {"name": "Jeremy Renner", "character": "Ian Donnelly"},
            {"name": "Forest Whitaker", "character": "Colonel Weber"},
            {"name": "Michael Stuhlbarg", "character": "Agent Halpern"},
        ],
        "crew_members": [{"name": "Denis Villeneuve", "job": "Director", "department": "Directing"}],
        "poster_path": "/pEzNVQfdzYDzVK0XqxERIw2x2se.jpg",
        "backdrop_path": "https://upload.wikimedia.org/wikipedia/en/d/df/Arrival%2C_Movie_Poster.jpg",
    },
    {
        "id": 545611,
        "title": "Everything Everywhere All at Once",
        "original_title": "Everything Everywhere All at Once",
        "overview": "An aging Chinese immigrant is swept up in an insane adventure, where she alone can save what's important to her by connecting with the lives she could have led in parallel universes.",
        "tagline": "The universe is so much bigger than you realize.",
        "status": "Released",
        "release_date": "2022-03-25",
        "year": 2022,
        "vote_average": 7.8,
        "vote_count": 6800,
        "popularity": 190.0,
        "budget": 25000000,
        "revenue": 143400000,
        "runtime": 139.0,
        "original_language": "en",
        "genres": ["Action", "Adventure", "Science Fiction"],
        "keywords": ["multiverse", "family", "martial arts", "absurdism"],
        "director": "Daniel Kwan",
        "cast_members": [
            {"name": "Michelle Yeoh", "character": "Evelyn Wang"},
            {"name": "Ke Huy Quan", "character": "Waymond Wang"},
            {"name": "Stephanie Hsu", "character": "Joy Wang / Jobu Tupaki"},
            {"name": "Jamie Lee Curtis", "character": "Deirdre Beaubeirdre"},
        ],
        "crew_members": [{"name": "Daniel Kwan", "job": "Director", "department": "Directing"}],
        "poster_path": "/u68AjlvlutfEIcpmbYpKcdi09ut.jpg",
        "backdrop_path": "https://upload.wikimedia.org/wikipedia/en/1/1e/Everything_Everywhere_All_at_Once.jpg",
    },
]


def ingest_data(movies_path: Path = MOVIES_CSV, credits_path: Path = CREDITS_CSV, overwrite: bool = False) -> dict:
    """
    Load TMDB 5000 datasets, merge on movie ID, clean all fields,
    and seed SQLite database with indexes.
    """
    log.info("Starting TMDB ingestion from %s and %s", movies_path, credits_path)
    Base.metadata.create_all(bind=engine)

    if not movies_path.exists() or not credits_path.exists():
        raise FileNotFoundError(f"Missing dataset files: {movies_path} or {credits_path}")

    # Read CSVs
    movies_df = pd.read_csv(movies_path)
    credits_df = pd.read_csv(credits_path)

    movies_df = movies_df.drop_duplicates("id")
    credits_df = credits_df.drop_duplicates("movie_id")

    # Merge on movie ID
    merged = movies_df.merge(
        credits_df[["movie_id", "cast", "crew"]],
        left_on="id",
        right_on="movie_id",
        how="left"
    ).drop(columns=["movie_id"])

    # Clean numeric fields
    for col in ("budget", "revenue", "runtime"):
        merged[col] = pd.to_numeric(merged[col], errors="coerce").replace(0, np.nan)
    merged["vote_count"] = pd.to_numeric(merged["vote_count"], errors="coerce").fillna(0).astype(int)
    merged["vote_average"] = pd.to_numeric(merged["vote_average"], errors="coerce")
    merged["popularity"] = pd.to_numeric(merged["popularity"], errors="coerce").fillna(0.0)

    # Dates and years
    dates = pd.to_datetime(merged["release_date"], errors="coerce")
    merged["year"] = dates.dt.year
    merged["clean_release_date"] = dates.dt.date

    # Extract JSON fields
    merged["title"] = merged["title"].fillna("Untitled").astype(str)
    merged["genres_list"] = merged["genres"].map(extract_names)
    merged["keywords_list"] = merged["keywords"].map(extract_names)
    merged["companies_list"] = merged["production_companies"].map(extract_names)
    merged["countries_list"] = merged["production_countries"].map(extract_names)
    merged["director_name"] = merged["crew"].map(extract_director)
    merged["cast_list"] = merged["cast"].map(lambda c: extract_cast(c, 20))
    merged["crew_list"] = merged["crew"].map(lambda c: extract_crew(c, 20))

    def _val(v):
        if v is None:
            return None
        if not isinstance(v, (list, str)) and pd.isna(v):
            return None
        return v

    db: Session = SessionLocal()
    try:
        existing_ids = set(db.scalars(select(Movie.id)).all())
        records_to_insert = []

        for _, row in merged.iterrows():
            mid = int(row["id"])
            if mid in existing_ids and not overwrite:
                continue

            r_date = row["clean_release_date"]
            release_d = r_date if (r_date and not pd.isna(r_date)) else None

            # Check curated poster map
            p_path = None
            b_path = None
            if mid in CURATED_POSTERS:
                p_path = CURATED_POSTERS[mid].get("poster")
                b_path = CURATED_POSTERS[mid].get("backdrop")

            record = {
                "id": mid,
                "title": str(row["title"]),
                "original_title": _val(row.get("original_title")),
                "overview": _val(row.get("overview")),
                "tagline": _val(row.get("tagline")),
                "status": _val(row.get("status")) or "Released",
                "release_date": release_d,
                "year": None if _val(row["year"]) is None else int(row["year"]),
                "vote_average": _val(row["vote_average"]),
                "vote_count": int(row["vote_count"]),
                "popularity": _val(row["popularity"]),
                "budget": None if _val(row["budget"]) is None else int(row["budget"]),
                "revenue": None if _val(row["revenue"]) is None else int(row["revenue"]),
                "runtime": _val(row["runtime"]),
                "original_language": _val(row.get("original_language")),
                "genres": row["genres_list"],
                "keywords": row["keywords_list"],
                "production_companies": row["companies_list"],
                "production_countries": row["countries_list"],
                "director": _val(row["director_name"]),
                "cast_members": row["cast_list"],
                "crew_members": row["crew_list"],
                "poster_path": p_path,
                "backdrop_path": b_path,
                "last_edited_by": "System Pipeline",
            }

            if mid in existing_ids and overwrite:
                db.merge(Movie(**record))
            else:
                records_to_insert.append(record)

        # Batch insert
        batch_size = 500
        for i in range(0, len(records_to_insert), batch_size):
            batch = records_to_insert[i:i + batch_size]
            db.bulk_insert_mappings(Movie, batch)
            db.commit()

        # Insert modern mockup-featured films if missing
        featured_added = 0
        current_ids = set(db.scalars(select(Movie.id)).all())
        for film in MOCKUP_FEATURED_FILMS:
            if film["id"] not in current_ids:
                film_copy = dict(film)
                if isinstance(film_copy["release_date"], str):
                    film_copy["release_date"] = date.fromisoformat(film_copy["release_date"])
                film_copy["last_edited_by"] = "System Pipeline"
                db.add(Movie(**film_copy))
                featured_added += 1
        if featured_added > 0:
            db.commit()

        total_count = db.scalar(select(func.count(Movie.id)))
        log.info("Ingestion completed. Total movies in DB: %d", total_count)
        return {
            "total_movies": total_count,
            "inserted": len(records_to_insert) + featured_added,
            "already_existed": len(existing_ids),
        }
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ingest_data()
