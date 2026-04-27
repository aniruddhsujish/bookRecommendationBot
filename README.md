# ShelfSense

A semantic book recommendation engine that finds books similar to ones you love, explains *why* they're similar, and learns your taste over time through thumbs up/down feedback.

## What it does

- **Seeded recommendations** — enter any book title and get 5 semantically similar books with AI-generated explanations of what they share and how they differ
- **On-demand lookup** — if a book isn't in the local database, it's fetched live from Google Books, embedded, and stored for future queries
- **Taste profile** — rate books with thumbs up or down; the system builds a personal taste vector from your ratings
- **Discover** — get recommendations with no seed book, purely based on your accumulated taste profile

## Architecture

```
Google Books API
       │
       ▼
Async Ingestion Pipeline
       │  rate limiting, pagination, dedup, checkpointing
       ▼
sentence-transformers (all-MiniLM-L6-v2)
       │  local embeddings, no API cost
       ▼
Qdrant Vector DB
       │  HNSW index, cosine similarity, local persistence
       ▼
FastAPI Backend
├── POST /api/recommend   →  vector search + Claude explanation
├── POST /api/rate        →  saves to SQLite
├── GET  /api/discover    →  taste vector search
└── POST /api/explain     →  Claude API
       │
       ▼
Next.js Frontend

Taste Profile (SQLite → ratings → taste vector → Qdrant)
liked centroid − 0.5 × disliked centroid
```

## Tech Stack

| Layer | Tool |
|---|---|
| Data source | Google Books API |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Vector DB | Qdrant (local) |
| LLM | Claude Haiku (Anthropic) |
| Structured output | instructor + Pydantic |
| Backend | FastAPI + Uvicorn |
| Ratings storage | SQLite |
| Frontend | Next.js + Tailwind CSS |

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Books API key
- Anthropic API key

### Backend setup

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

Create a `.env` file from `.env.example` and add your API keys.

### Running ingestion

Fetches books from Google Books API across 140+ genres and subjects. Respects the free tier daily quota of 1,000 requests — uses checkpointing to resume across multiple days.

```bash
python run_ingestion.py
```

### Generating embeddings

Run after ingestion completes. Embeds all book descriptions and stores them in Qdrant.

```bash
python run_embedding.py
```

### Starting the API

```bash
uvicorn api.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend available at `http://localhost:3000`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/recommend` | Get 5 similar books for a given title |
| POST | `/api/rate` | Rate a book (1 = thumbs up, -1 = thumbs down) |
| GET | `/api/discover` | Get recommendations based on taste profile |
| POST | `/api/explain` | Explain similarity between two books |

## How the taste profile works

Every book is represented as a 384-dimensional vector encoding its semantic meaning. When you rate books, the system computes:

```
taste_vector = mean(liked book vectors) − 0.5 × mean(disliked book vectors)
```

This vector points toward the region of embedding space you enjoy. The `/discover` endpoint finds the books closest to this vector that you haven't rated yet.

## Notes

- Ingestion runs over multiple days due to Google Books API free tier quota (1,000 requests/day)
- The embedding model runs fully locally — no cost, no data sent externally
- Any book not in the local database is fetched on-demand from Google Books when searched
- Book database is currently sourced from Google Books API. Open Library integration is planned to significantly expand coverage with a comprehensive catalog dump.
