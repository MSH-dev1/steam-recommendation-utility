"""Steam OpenID login endpoints. Sessions are added in step 2c."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.services.steam_auth import build_login_redirect_url, extract_steam_id, verify_callback
from app.services.user_service import get_or_create_user

router = APIRouter(prefix="/auth/steam", tags=["auth"])


@router.get("/login")
def login() -> RedirectResponse:
    settings = get_settings()
    return RedirectResponse(build_login_redirect_url(settings.base_url))


@router.get("/callback")
def callback(request: Request, db: Session = Depends(get_db)) -> dict[str, object]:
    params = dict(request.query_params)

    if not verify_callback(params):
        raise HTTPException(status_code=401, detail="Steam could not verify this login")

    claimed_id = params.get("openid.claimed_id", "")
    try:
        steam_id = extract_steam_id(claimed_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    user = get_or_create_user(db, steam_id)
    return {"id": user.id, "steam_id": user.steam_id}
