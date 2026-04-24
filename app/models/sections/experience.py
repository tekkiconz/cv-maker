from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants.limits import (
    EXPERIENCE_DATE_MAX_LEN,
    EXPERIENCE_ENTRY_CONTENT_MAX_LEN,
    EXPERIENCE_ORGANISATION_MAX_LEN,
    EXPERIENCE_TITLE_MAX_LEN,
)
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.profile import Profile


def _utcnow() -> datetime:
    return datetime.now(tz=UTC)


class ExperienceSection(Base):
    __tablename__ = "experience_sections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(EXPERIENCE_TITLE_MAX_LEN), nullable=False)
    organisation: Mapped[str | None] = mapped_column(String(EXPERIENCE_ORGANISATION_MAX_LEN), nullable=True)
    start_date: Mapped[str | None] = mapped_column(String(EXPERIENCE_DATE_MAX_LEN), nullable=True)
    end_date: Mapped[str | None] = mapped_column(String(EXPERIENCE_DATE_MAX_LEN), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    display_order: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )
    entries: Mapped[list[ExperienceEntry]] = relationship(
        "ExperienceEntry", cascade="all, delete-orphan"
    )
    profile: Mapped[Profile] = relationship("Profile", back_populates="experience_sections")


class ExperienceEntry(Base):
    __tablename__ = "experience_entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    section_id: Mapped[int] = mapped_column(
        ForeignKey("experience_sections.id"), nullable=False
    )
    content: Mapped[str] = mapped_column(String(EXPERIENCE_ENTRY_CONTENT_MAX_LEN), nullable=False)
    display_order: Mapped[int] = mapped_column(default=0, nullable=False)
