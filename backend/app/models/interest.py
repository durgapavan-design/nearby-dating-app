import uuid

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

user_interests = Table(
    "user_interests",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("interest_id", UUID(as_uuid=True), ForeignKey("interests.id", ondelete="CASCADE"), primary_key=True),
)


class Interest(Base):
    __tablename__ = "interests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(60), nullable=False)

    users = relationship("User", secondary=user_interests, back_populates="interests")
