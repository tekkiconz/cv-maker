from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants.limits import PROFILE_DESCRIPTION_MAX_LEN, PROFILE_NAME_MAX_LEN
from app.models.base import Base


def _utcnow() -> datetime:
    return datetime.now(tz=UTC)


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(PROFILE_NAME_MAX_LEN), nullable=False)
    description: Mapped[str | None] = mapped_column(
        String(PROFILE_DESCRIPTION_MAX_LEN), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )
    contacts: Mapped[list[ProfileContact]] = relationship(
        "ProfileContact", cascade="all, delete-orphan", back_populates="profile"
    )


class ProfileContact(Base):
    __tablename__ = "profile_contacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=False)

    profile: Mapped[Profile] = relationship("Profile", back_populates="contacts")
