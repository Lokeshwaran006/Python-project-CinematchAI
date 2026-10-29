# 🎬 CineMatch AI — Movie Recommendation & Discovery System

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4%2B-F7931E.svg)](https://scikit-learn.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-4169E1.svg)](https://supabase.com/)
[![Render](https://img.shields.io/badge/Render-Deployed%20Live-46E3B7.svg)](https://python-project-cinematchai.onrender.com)
[![Status](https://img.shields.io/badge/Status-Active%20%26%20Production%20Ready-success.svg)]()

> **Live Application URL:** [https://python-project-cinematchai.onrender.com](https://python-project-cinematchai.onrender.com)  
> **Course:** Advanced Python Programming (Project Review)  
> **Architecture:** Cloud-Native, Two-Tier Interconnected Web Architecture  

---

## 📌 Project Overview

**CineMatch AI** is a production-ready, full-stack movie intelligence platform built with **FastAPI**, **Scikit-Learn**, and **PostgreSQL (Supabase)**. It enables users to browse, search, and filter a catalog of **4,800+ movies** from the TMDB 5000 dataset with real-time content-based recommendations, high-resolution official TMDB posters, community reviews, and multi-parameter filtering.

The application forms part of an interconnected two-tier ecosystem sharing a synchronized PostgreSQL cloud database with a partner **Movie Analytics Dashboard**.

---

## 🌟 Key Features

### 1. 🤖 Content-Based Machine Learning Recommendation Engine
* **Metadata Soup Vectorization**: Aggregates narrative overview, weighted director names (x3), top cast members (x2), weighted genres (x2), and thematic keywords.
* **TF-IDF & Cosine Similarity**: Uses Scikit-Learn `TfidfVectorizer(max_features=10000)` and `linear_kernel` cosine similarity matrix computed in sub-second execution time.
* **Explainable AI (XAI)**: Generates clear, human-readable rationale pills explaining *why* a movie is recommended (e.g., *"Matches preference for Sci-Fi"*, *"Directed by Christopher Nolan"*, *"98% Taste Match"*).
* **Live Dynamic Re-Indexing**: Exposes `POST /api/reindex` to recalculate the TF-IDF vector matrix on-the-fly when new movies are added.

### 2. 🎨 Pixel-Perfect Dark Cinematic Interface
* **Hero Carousel Banner**: Showcases trending titles (*Interstellar*, *Inception*, *The Dark Knight*, *Dune*) with dynamic metadata, star ratings, and backdrop art.
* **"Recommended For You" Rail**: Horizontal scroll rail with taste match badges (`98% Match`), ratings, and quick watchlist toggles.
* **Multi-Attribute Filter Sidebar**:
  * Multi-genre checkboxes with real-time film counts.
  * Dual-thumb release year range slider (1980–2026).
  * Minimum rating slider (`0.0` to `10.0`).
  * International language selector chips (`English`, `French`, `Japanese`, `Hindi`, `Spanish`).
* **Critics' Review & Rating Pipeline**:
  * Interactive 10-star rating selector and smooth slider.
  * **Mandatory Critic Name validation** preventing anonymous submissions.
  * Spoiler warning toggle.
  * Non-destructive multi-review storage: preserves all submitted reviews independently.

### 3. 🖼️ Official TMDB Poster Enrichment Pipeline
* Integrates directly with the **The Movie Database (TMDB) API v3**.
* Features an automated background enrichment script that fetched official high-resolution poster paths for 4,560+ titles into PostgreSQL.
* Resilient offline SVG poster generator fallback ensures zero broken images.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Backend Framework** | FastAPI (ASGI), Starlette, Uvicorn |
| **Machine Learning** | Scikit-Learn (`TfidfVectorizer`, Cosine Similarity), NumPy, Pandas |
| **Database & ORM** | PostgreSQL (Supabase), SQLAlchemy 2.0, Psycopg2-binary |
| **Frontend UI** | HTML5, Modern CSS3 (Glassmorphism, CSS Grid, Flexbox), Vanilla JavaScript |
| **Templates** | Jinja2 Server-Side Rendering |
| **External APIs** | The Movie Database (TMDB) API v3 |
| **Deployment** | Render.com Web Services (Python 3.11 Environment) |

---

## 🤖 Generative AI Prompts Used During Development

As part of the development lifecycle, generative AI was utilized to design, architect, engineer, and troubleshoot components across the software stack. Below are the key structured prompts employed:

### 1. Architectural Design & Shared Cloud Database
> *"Design a modular, production-ready FastAPI application for a movie recommendation system that interfaces with a shared Supabase PostgreSQL database. Create SQLAlchemy ORM models for Movies, ReviewRatings, and Watchlists with complete schema definitions matching the TMDB 5000 dataset. Ensure support for dynamic connection URL normalization (handling URL-encoded credentials) and seamless fallback to SQLite for local development."*

### 2. Machine Learning Recommendation Engine & Explainability
> *"Implement a content-based recommendation engine in Python using Scikit-Learn's TfidfVectorizer and pairwise cosine similarity. Construct a composite 'metadata soup' by tokenizing movie overviews, weighting directors (x3), top cast members (x2), genres (x2), and keywords. Optimize the vectorizer to index 4,800+ films efficiently and implement an Explainable AI function that produces human-readable recommendation rationale pills (e.g. 'Matches preference for Sci-Fi', 'Director Christopher Nolan')."*

### 3. Glassmorphic Dark UI & Frontend Interactivity
> *"Generate a responsive, dark-mode cinematic user interface using Jinja2 templates, vanilla CSS, and JavaScript. Implement: 1) A hero carousel displaying trending movies with synopsis and IMDb ratings; 2) A horizontal scrolling recommendation rail with match percentage badges; 3) A dynamic left-hand filter sidebar featuring synchronized dual-slider release years, genre checkboxes with live movie count badges, and language chips; 4) A 10-star critic rating widget with character-counted reviews."*

### 4. Mandatory Critic Name Validation & Review Preservation
> *"Refactor the user review submission flow in both the FastAPI backend (`user.py`, `schemas.py`) and frontend JavaScript (`app.js`). Enforce critic name as a mandatory field; if left blank, highlight the input in red and prevent submission. Modify the database persistence logic so every review is saved as an independent historical record rather than overwriting previous entries."*

### 5. Automated TMDB Poster Enrichment Pipeline
> *"Write a standalone Python script using `requests` and `SQLAlchemy` that connects to the Supabase PostgreSQL database, scans all movie records missing a `poster_path`, queries the TMDB API v3 (`/search/movie`), extracts high-resolution official poster paths, and commits them in batches. Implement retry handling, rate limiting, and progress logging."*

### 6. Cloud Deployment & Production Configuration
> *"Configure CineMatch AI for cloud deployment on Render.com. Create a `render.yaml` specification and update `requirements.txt` with all production binaries (`psycopg2-binary`, `scikit-learn`, `uvicorn`). Structure environment variables (`DATABASE_URL`, `TMDB_API_KEY`, `SECRET_KEY`, `CORS_ORIGINS`) to run securely with zero hardcoded credentials."*

---

## 📂 Project Directory Structure

```text
Python-project-CinematchAI/
├── render.yaml               # Render Infrastructure-as-Code deployment spec
├── requirements.txt          # Production Python package dependencies
├── README.md                 # Project documentation & evaluation details
└── app/
    ├── __init__.py
    ├── config.py             # Environment configuration, DB URLs, & TMDB keys
    ├── database.py           # SQLAlchemy engine & session factory
    ├── ingest.py             # CSV-to-Database ingestion logic
    ├── main.py               # FastAPI application entry point & lifecycle hooks
    ├── models.py             # Database ORM models (Movie, ReviewRating, Watchlist)
    ├── posters.py            # TMDB poster resolution & offline SVG fallback
    ├── recommender.py        # Scikit-Learn Content-Based Recommendation Engine
    ├── schemas.py            # Pydantic request/response validation schemas
    ├── routers/
    │   ├── analytics.py      # Analytical data endpoints for partner integration
    │   ├── movies.py         # Catalog search, filter, and CRUD endpoints
    │   ├── recommend.py      # Recommendation API endpoints
    │   ├── reindex.py        # Vector re-indexing endpoint (/api/reindex)
    │   ├── user.py           # Reviews, ratings, and watchlist handlers
    │   └── views.py          # HTML template routes (Discover, Detail, Watchlist)
    ├── static/
    │   ├── css/
    │   │   └── style.css     # Dark cinematic styling & responsive layouts
    │   └── js/
    │       └── app.js        # Dynamic DOM updates, filter events, & review logic
    └── templates/
        ├── base.html         # Base layout with navbar, CRUD modal, and footer
        ├── detail.html       # Movie detail, recommendation cards, & review box
        ├── discover.html     # Advanced discovery engine & filter catalog
        ├── index.html        # Home page & hero carousel
        ├── partner_bridge.html # Inter-application integration dashboard
        └── watchlist.html    # User's personal saved watchlist
