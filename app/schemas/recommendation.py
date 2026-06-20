"""Recommendation schemas. Stable outward-facing contract."""

from pydantic import BaseModel


class Recommendation(BaseModel):
    """A single recommended game. Its shape does not depend on what produced it
    (stub / content-based / LLM) - the implementation changes, the contract doesn't."""

    appid: int | None
    name: str
    reason: str
