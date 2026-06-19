"""FastAPI entrypoint. Assembles the app and wires up the routes."""

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import get_settings
from app.routes import auth, health, recommendations

settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    https_only=False,
    same_site="lax",
)

app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(recommendations.router, prefix=settings.api_v1_prefix)
app.include_router(auth.router, prefix=settings.api_v1_prefix)


@app.get("/")
def root() -> dict[str, str]:
    return {"app": settings.app_name, "docs": "/docs"}
