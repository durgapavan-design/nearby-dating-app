import uuid

from pydantic import BaseModel

from app.models.swipe import SwipeAction


class SwipeIn(BaseModel):
    target_id: uuid.UUID
    action: SwipeAction


class SwipeResult(BaseModel):
    matched: bool
    match_id: uuid.UUID | None = None
