from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.constants.limits import (
    EDUCATION_DATE_MAX_LEN,
    EDUCATION_ENTRY_CONTENT_MAX_LEN,
    EDUCATION_ORGANISATION_MAX_LEN,
    EDUCATION_TITLE_MAX_LEN,
)


class EducationSectionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=EDUCATION_TITLE_MAX_LEN)
    organisation: str | None = Field(default=None, max_length=EDUCATION_ORGANISATION_MAX_LEN)
    start_date: str | None = Field(default=None, max_length=EDUCATION_DATE_MAX_LEN)
    end_date: str | None = Field(default=None, max_length=EDUCATION_DATE_MAX_LEN)
    is_enabled: bool = True
    display_order: int = 0


class EducationEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    section_id: int
    content: str
    display_order: int


class EducationSectionRead(BaseModel):
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
    entries: list[EducationEntryRead] = []


class EducationSectionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=EDUCATION_TITLE_MAX_LEN)
    organisation: str | None = Field(default=None, max_length=EDUCATION_ORGANISATION_MAX_LEN)
    start_date: str | None = Field(default=None, max_length=EDUCATION_DATE_MAX_LEN)
    end_date: str | None = Field(default=None, max_length=EDUCATION_DATE_MAX_LEN)
    is_enabled: bool | None = None
    display_order: int | None = None


class EducationEntryCreate(BaseModel):
    content: str = Field(min_length=1, max_length=EDUCATION_ENTRY_CONTENT_MAX_LEN)
    display_order: int = 0


class EducationEntryUpdate(BaseModel):
    content: str | None = Field(
        default=None, min_length=1, max_length=EDUCATION_ENTRY_CONTENT_MAX_LEN
    )
    display_order: int | None = None
