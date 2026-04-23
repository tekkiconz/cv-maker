from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.constants.limits import PROFILE_DESCRIPTION_MAX_LEN, PROFILE_NAME_MAX_LEN
from app.models.base import Base


def _utcnow() -> datetime:
    return datetime.now(tz=UTC)


class Profile(Base):
    __tablename__ = "profiles"
    # TODO(Story 2.1): add relationship("ExperienceSection", cascade="all, delete-orphan")
    # once ExperienceSection model exists — satisfies AC 3 cascade delete requirement

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
