# Steam Recommendation Utility

A web app that recommends Steam games based on a user's library
(what they own, what they've liked, how many hours they've played). Hybrid approach:
content-based filtering + an LLM layer on top of the data.

Stack: FastAPI + Jinja2 + HTMX, PostgreSQL (SQLAlchemy + Alembic), Docker.

## Running

```bash
cp .env.example .env       # then fill in the keys below
docker compose up --build
```

`.env` needs two API keys to work fully:
- `STEAM_API_KEY` - get one at https://steamcommunity.com/dev/apikey
- `RAWG_API_KEY` - get one at https://rawg.io/apidocs

`SESSION_SECRET` and `BASE_URL` are also required; see the comments in `.env.example`.

- App: http://localhost:8000
- Swagger (API docs): http://localhost:8000/docs
- Health check: http://localhost:8000/api/v1/health

Health returns `{"status": "ok", "db": "ok"}` when the service is up and can reach the DB.

## Project layout (layered architecture)

```
app/
├── core/        # config (env via pydantic-settings)
├── db/          # DB connection, base model class
├── models/      # User, Game, Genre, Tag, UserGame, GameGenre, GameTag
├── schemas/     # Pydantic schemas (contracts)
├── services/    # business logic, HTTP-agnostic
│   ├── steam_client.py, rawg_client.py       # external API wrappers
│   ├── library_sync.py, metadata_sync.py,    # sync/enrichment jobs (TTL-based)
│   │   catalog_sync.py
│   └── recommendations/   # recommender boundary: base / stub / content-based / factory
└── routes/      # HTTP layer
```

Recommendations are always called through `get_recommender().get_recommendations(user_id)`.
The content-based implementation is active now (the stub is kept around but no longer
wired up); an LLM layer can replace it later behind the same boundary, without touching
the rest of the codebase.

Game metadata provided by RAWG (rawg.io).

## Current stage

Steps 1-2 are done (skeleton, User model, Steam OpenID login, server-side sessions).

Also done:
- **Step 3**: `SteamClient` wrapper for the Steam Web API (owned games with playtime,
  player profile)
- **Step 4**: library persistence in the DB, with TTL-based sync
- **Step 5**: RAWG metadata integration (genres/tags), game catalog population (~500
  games), and a content-based recommender with IDF-weighted genre/tag similarity
  (replaces the stub)

Next up: step 6 - frontend (Jinja2/HTMX pages).

## Development

```bash
ruff check app/
black app/
```
