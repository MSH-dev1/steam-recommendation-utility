"""Steam OpenID login endpoints, plus session-based login state."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.steam_auth import build_login_redirect_url, extract_steam_id, verify_callback
from app.services.user_service import get_or_create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/steam/login")
def login() -> RedirectResponse:
    settings = get_settings()
    return RedirectResponse(build_login_redirect_url(settings.base_url))


@router.get("/steam/callback")
def callback(request: Request, db: Session = Depends(get_db)) -> RedirectResponse:
    params = dict(request.query_params)

    if not verify_callback(params):
        raise HTTPException(status_code=401, detail="Steam could not verify this login")

    claimed_id = params.get("openid.claimed_id", "")
    try:
        steam_id = extract_steam_id(claimed_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    user = get_or_create_user(db, steam_id)
    request.session["user_id"] = user.id
    return RedirectResponse("/")


@router.get("/me")
def me(user: User | None = Depends(get_current_user)) -> dict[str, object]:
    if user is None:
        raise HTTPException(status_code=401, detail="Not logged in")
    return {"id": user.id, "steam_id": user.steam_id}


@router.get("/logout")
def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse("/")
