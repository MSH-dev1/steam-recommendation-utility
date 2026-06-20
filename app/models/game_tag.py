"""Many-to-many link between games and tags."""

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class GameTag(Base):
    """A single (game, tag) association."""

    __tablename__ = "game_tags"
    __table_args__ = (UniqueConstraint("game_id", "tag_id", name="uq_game_tags_game_tag"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False, index=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), nullable=False, index=True)
