"""ORM models. Base lives in app.db.session."""

from app.models.genre import Genre  # noqa: F401
from app.models.tag import Tag  # noqa: F401
from app.models.game import Game  # noqa: F401
from app.models.game_genre import GameGenre  # noqa: F401
from app.models.game_tag import GameTag  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.user_game import UserGame  # noqa: F401

