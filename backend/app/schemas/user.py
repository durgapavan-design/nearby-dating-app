import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.user import Gender, LocationSource, ShowMe


class InterestOut(BaseModel):
    id: uuid.UUID
    name: str
    category: str

    model_config = ConfigDict(from_attributes=True)


class PhotoOut(BaseModel):
    id: uuid.UUID
    url: str
    position: int
    is_primary: bool

    model_config = ConfigDict(from_attributes=True)


class ProfileUpdate(BaseModel):
    name: str | None = None
    birthdate: date | None = None
    gender: Gender | None = None
    show_me: ShowMe | None = None
    bio: str | None = None
    city: str | None = None


class MeOut(BaseModel):
    id: uuid.UUID
    phone_number: str
    name: str | None
    birthdate: date | None
    gender: Gender | None
    show_me: ShowMe | None
    bio: str | None
    city: str | None
    location_source: LocationSource
    profile_completed: bool
    photos: list[PhotoOut] = []
    interests: list[InterestOut] = []

    model_config = ConfigDict(from_attributes=True)


class InterestIdsUpdate(BaseModel):
    interest_ids: list[uuid.UUID]


class DiscoveryProfileOut(BaseModel):
    id: uuid.UUID
    name: str | None
    age: int | None
    bio: str | None
    city: str | None
    photos: list[PhotoOut] = []
    interests: list[InterestOut] = []
    shared_interest_count: int = 0
