"""Game model. Catalog entries from RAWG may have no Steam appid at all."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.game_genre import GameGenre
from app.models.game_tag import GameTag
from app.models.genre import Genre
from app.models.tag import Tag


class Game(Base):
    """A game, optionally tied to a Steam appid (catalog-only games have none)."""

    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    appid: Mapped[int | None] = mapped_column(nullable=True, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    # RAWG enrichment state. rawg_id is null until matched (or never, if rawg_match_failed).
    rawg_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    metadata_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    rawg_match_failed: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )

    genres: Mapped[list[Genre]] = relationship(secondary=GameGenre.__table__, viewonly=False)
    tags: Mapped[list[Tag]] = relationship(secondary=GameTag.__table__, viewonly=False)
