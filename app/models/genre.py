"""Genre lookup table, populated from RAWG metadata."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Genre(Base):
    """A game genre (e.g. 'Action', 'RPG'), shared across games."""

    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
