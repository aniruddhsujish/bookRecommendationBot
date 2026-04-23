# Book Recommender

A semantic book recommendation engine that finds books similar to ones you love, explaining *why* they're similar, also learns your taste over time through thumbs up/ thumbs down feedback

## What it does

- **Seeded recommendations** - enter any book title and get 5 semantically similar books with AI-generated explanations of what they share and how they differ
- **On-demand lookup** - if a book isn't in the local database, it's fetched live from Google Books, and stored locally for future queries
- **Taste profile** - rate books with thumbs up or down, the system then builds a personal taste vector from your ratings
- **Discover** - get recommendations with no seed book, purely based on your accumulated taste profile

## Architecture

  Google Books API
        │
        ▼
  Async Ingestion Pipeline
  (rate limiting, pagination, deduplication,checkpointing)
        │
        ▼
  sentence-transformers (all-MiniLM-L6-v2)
  (local embedding model, no API cost)
        │
        ▼
  Qdrant Vector DB (local persistence)
  (HNSW index, cosine similarity, payload filtering)
        │                          ▲
        ▼                          │ taste vector
  FastAPI Backend          SQLite (ratings)
    ├── /api/recommend     Taste Profile Service
    ├── /api/discover      (liked centroid − 0.5 × disliked centroid)
    ├── /api/rate
    └── /api/explain  →  Claude API (similarity explanation)
        │
        ▼
  Next.js Frontend

## Tech Stack

Data Source -> Google Books API
Embeddings -> sentence-transformers (`all-MiniLM-L6-v2`)
Vector DB -> Qdrant(Local)
LLM -> Claude Haiku
Backend -> FastAPI + Uvicorn
Ratings storage -> SQLite
Frontend -> In progress

## Getting Started

### Prerequisites

- Python 3.11+
- Google Books API key
- Anthropic API Key

### Setup

```bash
# clone the repo
git clone <repo-url>
cd bookRecommendationBot

# create and activate virtual environment
python -m venv venv
source venv/bin/activate

# install dependencies
pip install -r requirements.txt
```

Create a .env file from .env.example and add your API keys there

#### Running Ingestion

Fetches books from Google Books API across 140+ genres and subjects. Respects the free tier daily quota of 1000 requests - uses checkpointing to resume across multiple days

```bash
python run_ingestion.py
```

### Generating embeddings

Run after ingestion completes. embeds all book descriptions and stores them in Qdrant.

```bash
python run_embedding.py
```

### Starting the API

```bash
uvicorn api.main:app --reload --port 8000
```

API docs available at http://localhost:8000/docs

## How the taste profile works

Every book is represented as a 384-dimensional vector encoding its semantic meaning. When you rate books, the system computes:

taste_vector = mean(liked book vectors) - 0.5 * mean(disliked book vectors)

This vector points toward the region og embedding space you enjoy. The /discover endpoint finds the books closest to this vector that you haven't rated yet

## Notes

- Ingestion runs over multiple days due to Google Books API free tier quota (1000 request/day)
- The embedding model runs locally
- Any book not in the local database is fetched on-demand from Google Books when searched
- Frontend is currently a work-in-progress - the backend API is functional and testable via '/docs'