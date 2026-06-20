"""Shared genre/tag lookup-or-create helpers, used by both metadata_sync and catalog_sync."""

from sqlalchemy.orm import Session

from app.models.genre import Genre
from app.models.tag import Tag


def get_or_create_genre(db: Session, name: str) -> Genre:
    genre = db.query(Genre).filter(Genre.name == name).first()
    if genre is None:
        genre = Genre(name=name)
        db.add(genre)
        db.flush()
    return genre


def get_or_create_tag(db: Session, name: str) -> Tag:
    tag = db.query(Tag).filter(Tag.name == name).first()
    if tag is None:
        tag = Tag(name=name)
        db.add(tag)
        db.flush()
    return tag
