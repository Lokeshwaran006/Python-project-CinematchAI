import os
from pathlib import Path

# Paths
APP_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = APP_DIR.parent
DATA_DIR = WORKSPACE_DIR / "datasets"
MOVIES_CSV = DATA_DIR / "tmdb_5000_movies.csv"
CREDITS_CSV = DATA_DIR / "tmdb_5000_credits.csv"


def _load_env_file(path: Path) -> None:
    """Read key-value pairs from .env file into os.environ."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


# Load root .env if present
_load_env_file(WORKSPACE_DIR / ".env")


def _normalize_db_url(url: str) -> str:
    """Normalize Supabase/PostgreSQL connection URLs for SQLAlchemy and safely URL-encode passwords."""
    import urllib.parse
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://") and not url.startswith("postgresql+"):
        url = "postgresql+psycopg2://" + url[len("postgresql://"):]

    # Safely handle passwords containing @ or special characters
    if "://" in url and url.count("@") > 1:
        scheme, rest = url.split("://", 1)
        last_at = rest.rfind("@")
        user_pwd = rest[:last_at]
        host_db = rest[last_at + 1:]
        if ":" in user_pwd:
            user, pwd = user_pwd.split(":", 1)
            url = f"{scheme}://{user}:{urllib.parse.quote_plus(pwd)}@{host_db}"
    return url


# Shared database: defaults to local SQLite if DATABASE_URL is not set or placeholder password
DB_FILE = WORKSPACE_DIR / "cinematch.db"
raw_db_url = os.environ.get("DATABASE_URL")
if not raw_db_url or "YOUR_PASSWORD" in raw_db_url or "YOUR_ACTUAL_PASSWORD" in raw_db_url or "YOUR-PASSWORD" in raw_db_url:
    raw_db_url = f"sqlite:///{DB_FILE.as_posix()}"
DATABASE_URL = _normalize_db_url(raw_db_url)

# Partner analytics dashboard URL
PARTNER_URL = os.environ.get("PARTNER_URL", "http://localhost:8001")

# TMDB CDN Configuration
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/original"
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "8265bd1679663a7ea12ac168da84d2e8")

# Application settings
APP_NAME = "CineMatch AI"
APP_DESCRIPTION = "Movie Recommendation and Discovery System"
SECRET_KEY = os.environ.get("SECRET_KEY", "cinematch-secret-key-prod-2026")
CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "*").split(",") if o.strip()]
