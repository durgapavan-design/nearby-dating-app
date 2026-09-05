import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Gender(str, enum.Enum):
    male = "male"
    female = "female"
    non_binary = "non_binary"
    other = "other"


class ShowMe(str, enum.Enum):
    male = "male"
    female = "female"
    everyone = "everyone"


class LocationSource(str, enum.Enum):
    manual = "manual"
    gps = "gps"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)

    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    birthdate: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender, name="gender"), nullable=True)
    show_me: Mapped[ShowMe | None] = mapped_column(Enum(ShowMe, name="show_me"), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location_source: Mapped[LocationSource] = mapped_column(
        Enum(LocationSource, name="location_source"), default=LocationSource.manual, nullable=False
    )
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    profile_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    photos = relationship("Photo", back_populates="user", cascade="all, delete-orphan", order_by="Photo.position")
    interests = relationship("Interest", secondary="user_interests", back_populates="users")
