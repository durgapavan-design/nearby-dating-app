import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class MessageIn(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class MessageOut(BaseModel):
    id: uuid.UUID
    match_id: uuid.UUID
    sender_id: uuid.UUID
    content: str
    created_at: datetime
    read_at: datetime | None
