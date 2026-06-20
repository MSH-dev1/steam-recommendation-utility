"""Temporary route to verify RAWG matching by hand. Removed after step 5a."""

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.models.user import User
from app.services.rawg_client import RawgClient

router = APIRouter(prefix="/rawg", tags=["rawg"])


@router.get("/search")
def search_rawg_game(name: str, user: User | None = Depends(get_current_user)) -> dict[str, object]:
    if user is None:
        raise HTTPException(status_code=401, detail="Not logged in")

    settings = get_settings()
    client = RawgClient(settings.rawg_api_key)
    game = client.search_game(name)

    if game is None:
        raise HTTPException(status_code=404, detail=f"No RAWG match for {name!r}")

    return game.model_dump()
