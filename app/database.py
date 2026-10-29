import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

log = logging.getLogger("cinematch.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

Base = declarative_base()


def get_db():
    """FastAPI dependency for obtaining a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all database tables if they do not exist and sync sequences."""
    Base.metadata.create_all(bind=engine)
    if not DATABASE_URL.startswith("sqlite"):
        try:
            from sqlalchemy import text
            from app.posters import CURATED_POSTERS
            with engine.connect() as conn:
                # 1. Sync serial sequences
                for tbl in ["reviews", "watchlist", "editors"]:
                    try:
                        conn.execute(text(f"""
                            SELECT setval(
                                pg_get_serial_sequence('{tbl}', 'id'),
                                COALESCE((SELECT MAX(id) FROM {tbl}), 1)
                            );
                        """))
                    except Exception:
                        pass

                # 2. Sync curated posters so partner app also has thumbnails
                try:
                    for mid, cinfo in CURATED_POSTERS.items():
                        p = cinfo.get("poster")
                        b = cinfo.get("backdrop")
                        if p:
                            conn.execute(
                                text("UPDATE movies SET poster_path = :p WHERE id = :id AND (poster_path IS NULL OR poster_path = '');"),
                                {"id": mid, "p": p}
                            )
                        if b:
                            conn.execute(
                                text("UPDATE movies SET backdrop_path = :b WHERE id = :id AND (backdrop_path IS NULL OR backdrop_path = '');"),
                                {"id": mid, "b": b}
                            )
                except Exception as pe:
                    log.warning("Poster sync note: %s", pe)

                conn.commit()
            log.info("PostgreSQL sequences and posters synchronized successfully.")
        except Exception as e:
            log.warning("Sequence/poster synchronization skipped: %s", e)
    log.info("Database schema initialized.")
