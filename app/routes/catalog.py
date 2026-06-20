"""Thin HTTP layer for catalog population. All logic lives in catalog_sync."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.catalog_sync import populate_catalog
from app.services.rawg_client import RawgClient

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.post("/populate")
def populate(
    target_count: int = 500,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    if user is None:
        raise HTTPException(status_code=401, detail="Not logged in")

    settings = get_settings()
    client = RawgClient(settings.rawg_api_key)
    return populate_catalog(db, client, target_count=target_count)
