# Steam Recommendation Utility

A web app that recommends Steam games based on a user's library
(what they own, what they've liked, how many hours they've played). Hybrid approach:
content-based filtering + an LLM layer on top of the data.

Stack: FastAPI + Jinja2 + HTMX, PostgreSQL (SQLAlchemy + Alembic), Docker.

## Running

```bash
cp .env.example .env       # adjust values if needed
docker compose up --build
```

- App: http://localhost:8000
- Swagger (API docs): http://localhost:8000/docs
- Health check: http://localhost:8000/api/v1/health

Health returns `{"status": "ok", "db": "ok"}` when the service is up and can reach the DB.

## Project layout (layered architecture)

```
app/
├── core/        # config (env via pydantic-settings)
├── db/          # DB connection, base model class
├── models/      # ORM models (User added in step 2)
├── schemas/     # Pydantic schemas (contracts)
├── services/    # business logic, HTTP-agnostic
│   └── recommendations/   # recommender boundary: base / stub / factory
└── routes/      # HTTP layer
```

Recommendations are always called through `get_recommender().get_recommendations(user_id)`.
The implementation (stub -> content-based -> LLM) changes behind this boundary
without touching the rest of the codebase.

## Current stage

Step 1 (skeleton: FastAPI, health check, Docker, Postgres, a stub recommender behind
an interface) and Step 2 (User model + migration, Steam OpenID login implemented
manually, server-side sessions with `/auth/me` and `/auth/logout`) are done.

Next up: steps 3-4 - fetch the logged-in user's Steam library via the Steam API and
persist it.

## Development

```bash
ruff check app/
black app/
```
