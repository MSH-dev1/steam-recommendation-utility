"""Tag lookup table, populated from RAWG metadata."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Tag(Base):
    """A free-form game tag (e.g. 'Singleplayer', 'Sandbox'), shared across games."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
