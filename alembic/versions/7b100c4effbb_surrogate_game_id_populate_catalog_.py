"""surrogate game id, populate catalog support

Revision ID: 7b100c4effbb
Revises: 0639bb4d14ef
Create Date: 2026-06-20 14:18:32.624298

Hand-written (not pure autogenerate): switches games' primary key from the
Steam appid to a surrogate id, since catalog games from RAWG have no Steam
appid. appid becomes a nullable, unique column. user_games/game_genres/
game_tags switch their FK from games.appid to games.id (column renamed to
game_id), with data backfilled before the old appid columns are dropped.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b100c4effbb'
down_revision: Union[str, None] = '0639bb4d14ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the old FKs into games.appid first: they implicitly depend on the
    # games_pkey index (appid), which must go before appid stops being the PK.
    op.drop_constraint("user_games_appid_fkey", "user_games", type_="foreignkey")
    op.drop_constraint("game_genres_appid_fkey", "game_genres", type_="foreignkey")
    op.drop_constraint("game_tags_appid_fkey", "game_tags", type_="foreignkey")

    # games: add surrogate id (SERIAL auto-backfills existing rows), make it
    # the new PK, and free up appid to be nullable.
    op.execute("ALTER TABLE games ADD COLUMN id SERIAL")
    op.drop_constraint("games_pkey", "games", type_="primary")
    op.create_primary_key("games_pkey", "games", ["id"])
    op.alter_column("games", "appid", existing_type=sa.Integer(), nullable=True)
    op.create_index(op.f("ix_games_appid"), "games", ["appid"], unique=True)

    # game_genres: switch appid -> game_id
    op.add_column("game_genres", sa.Column("game_id", sa.Integer(), nullable=True))
    op.execute(
        "UPDATE game_genres SET game_id = games.id "
        "FROM games WHERE game_genres.appid = games.appid"
    )
    op.alter_column("game_genres", "game_id", nullable=False)
    op.drop_constraint("uq_game_genres_appid_genre", "game_genres", type_="unique")
    op.drop_index("ix_game_genres_appid", table_name="game_genres")
    op.drop_column("game_genres", "appid")
    op.create_index(op.f("ix_game_genres_game_id"), "game_genres", ["game_id"], unique=False)
    op.create_unique_constraint(
        "uq_game_genres_game_genre", "game_genres", ["game_id", "genre_id"]
    )
    op.create_foreign_key(
        "game_genres_game_id_fkey", "game_genres", "games", ["game_id"], ["id"]
    )

    # game_tags: switch appid -> game_id
    op.add_column("game_tags", sa.Column("game_id", sa.Integer(), nullable=True))
    op.execute(
        "UPDATE game_tags SET game_id = games.id "
        "FROM games WHERE game_tags.appid = games.appid"
    )
    op.alter_column("game_tags", "game_id", nullable=False)
    op.drop_constraint("uq_game_tags_appid_tag", "game_tags", type_="unique")
    op.drop_index("ix_game_tags_appid", table_name="game_tags")
    op.drop_column("game_tags", "appid")
    op.create_index(op.f("ix_game_tags_game_id"), "game_tags", ["game_id"], unique=False)
    op.create_unique_constraint("uq_game_tags_game_tag", "game_tags", ["game_id", "tag_id"])
    op.create_foreign_key("game_tags_game_id_fkey", "game_tags", "games", ["game_id"], ["id"])

    # user_games: switch appid -> game_id
    op.add_column("user_games", sa.Column("game_id", sa.Integer(), nullable=True))
    op.execute(
        "UPDATE user_games SET game_id = games.id "
        "FROM games WHERE user_games.appid = games.appid"
    )
    op.alter_column("user_games", "game_id", nullable=False)
    op.drop_constraint("uq_user_games_user_appid", "user_games", type_="unique")
    op.drop_index("ix_user_games_appid", table_name="user_games")
    op.drop_column("user_games", "appid")
    op.create_index(op.f("ix_user_games_game_id"), "user_games", ["game_id"], unique=False)
    op.create_unique_constraint("uq_user_games_user_game", "user_games", ["user_id", "game_id"])
    op.create_foreign_key(
        "user_games_game_id_fkey", "user_games", "games", ["game_id"], ["id"]
    )


def downgrade() -> None:
    # user_games: restore appid, drop game_id
    op.add_column("user_games", sa.Column("appid", sa.Integer(), nullable=True))
    op.execute(
        "UPDATE user_games SET appid = games.appid "
        "FROM games WHERE user_games.game_id = games.id"
    )
    op.alter_column("user_games", "appid", nullable=False)
    op.drop_constraint("user_games_game_id_fkey", "user_games", type_="foreignkey")
    op.drop_constraint("uq_user_games_user_game", "user_games", type_="unique")
    op.drop_index(op.f("ix_user_games_game_id"), table_name="user_games")
    op.create_unique_constraint("uq_user_games_user_appid", "user_games", ["user_id", "appid"])
    op.create_index("ix_user_games_appid", "user_games", ["appid"], unique=False)
    op.create_foreign_key(
        "user_games_appid_fkey", "user_games", "games", ["appid"], ["appid"]
    )
    op.drop_column("user_games", "game_id")

    # game_tags: restore appid, drop game_id
    op.add_column("game_tags", sa.Column("appid", sa.Integer(), nullable=True))
    op.execute(
        "UPDATE game_tags SET appid = games.appid FROM games WHERE game_tags.game_id = games.id"
    )
    op.alter_column("game_tags", "appid", nullable=False)
    op.drop_constraint("game_tags_game_id_fkey", "game_tags", type_="foreignkey")
    op.drop_constraint("uq_game_tags_game_tag", "game_tags", type_="unique")
    op.drop_index(op.f("ix_game_tags_game_id"), table_name="game_tags")
    op.create_unique_constraint("uq_game_tags_appid_tag", "game_tags", ["appid", "tag_id"])
    op.create_index("ix_game_tags_appid", "game_tags", ["appid"], unique=False)
    op.create_foreign_key("game_tags_appid_fkey", "game_tags", "games", ["appid"], ["appid"])
    op.drop_column("game_tags", "game_id")

    # game_genres: restore appid, drop game_id
    op.add_column("game_genres", sa.Column("appid", sa.Integer(), nullable=True))
    op.execute(
        "UPDATE game_genres SET appid = games.appid "
        "FROM games WHERE game_genres.game_id = games.id"
    )
    op.alter_column("game_genres", "appid", nullable=False)
    op.drop_constraint("game_genres_game_id_fkey", "game_genres", type_="foreignkey")
    op.drop_constraint("uq_game_genres_game_genre", "game_genres", type_="unique")
    op.drop_index(op.f("ix_game_genres_game_id"), table_name="game_genres")
    op.create_unique_constraint(
        "uq_game_genres_appid_genre", "game_genres", ["appid", "genre_id"]
    )
    op.create_index("ix_game_genres_appid", "game_genres", ["appid"], unique=False)
    op.create_foreign_key(
        "game_genres_appid_fkey", "game_genres", "games", ["appid"], ["appid"]
    )
    op.drop_column("game_genres", "game_id")

    # games: restore appid as PK, drop surrogate id
    op.drop_index(op.f("ix_games_appid"), table_name="games")
    op.alter_column("games", "appid", existing_type=sa.Integer(), nullable=False)
    op.drop_constraint("games_pkey", "games", type_="primary")
    op.create_primary_key("games_pkey", "games", ["appid"])
    op.drop_column("games", "id")
