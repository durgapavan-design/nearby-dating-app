import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.user import PhotoOut


class MatchOut(BaseModel):
    match_id: uuid.UUID
    user_id: uuid.UUID
    name: str | None
    primary_photo: PhotoOut | None
    created_at: datetime
    last_message: str | None = None
    last_message_at: datetime | None = None


class LikedMeOut(BaseModel):
    user_id: uuid.UUID
    name: str | None
    primary_photo: PhotoOut | None
    liked_at: datetime
