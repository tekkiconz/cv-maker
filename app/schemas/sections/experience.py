from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.constants.limits import (
    EXPERIENCE_DATE_MAX_LEN,
    EXPERIENCE_ENTRY_CONTENT_MAX_LEN,
    EXPERIENCE_ORGANISATION_MAX_LEN,
    EXPERIENCE_TITLE_MAX_LEN,
)


class ExperienceSectionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=EXPERIENCE_TITLE_MAX_LEN)
    organisation: str | None = Field(default=None, max_length=EXPERIENCE_ORGANISATION_MAX_LEN)
    start_date: str | None = Field(default=None, max_length=EXPERIENCE_DATE_MAX_LEN)
    end_date: str | None = Field(default=None, max_length=EXPERIENCE_DATE_MAX_LEN)
    is_enabled: bool = True
    display_order: int = 0


class ExperienceEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    section_id: int
    content: str
    display_order: int


class ExperienceSectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profile_id: int
    title: str
    organisation: str | None
    start_date: str | None
    end_date: str | None
    is_enabled: bool
    display_order: int
    created_at: datetime
    updated_at: datetime
    entries: list[ExperienceEntryRead] = []


class ExperienceSectionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=EXPERIENCE_TITLE_MAX_LEN)
    organisation: str | None = None
    start_date: str | None = Field(default=None, max_length=EXPERIENCE_DATE_MAX_LEN)
    end_date: str | None = Field(default=None, max_length=EXPERIENCE_DATE_MAX_LEN)
    is_enabled: bool | None = None
    display_order: int | None = None


class ExperienceEntryCreate(BaseModel):
    content: str = Field(min_length=1, max_length=EXPERIENCE_ENTRY_CONTENT_MAX_LEN)
    display_order: int = 0


class ExperienceEntryUpdate(BaseModel):
    content: str | None = Field(
        default=None, min_length=1, max_length=EXPERIENCE_ENTRY_CONTENT_MAX_LEN
    )
    display_order: int | None = None
