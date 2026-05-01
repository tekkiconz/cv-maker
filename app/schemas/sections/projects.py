from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants.limits import (
    PROJECT_DATE_MAX_LEN,
    PROJECT_ENTRY_CONTENT_MAX_LEN,
    PROJECT_ORGANISATION_MAX_LEN,
    PROJECT_TITLE_MAX_LEN,
)


class ProjectSectionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=PROJECT_TITLE_MAX_LEN)
    organisation: str | None = Field(default=None, min_length=1, max_length=PROJECT_ORGANISATION_MAX_LEN)
    start_date: str | None = Field(default=None, min_length=1, max_length=PROJECT_DATE_MAX_LEN)
    end_date: str | None = Field(default=None, min_length=1, max_length=PROJECT_DATE_MAX_LEN)
    is_enabled: bool = True
    display_order: int = Field(default=0, ge=0)


class ProjectEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    section_id: int
    content: str
    display_order: int
    created_at: datetime
    updated_at: datetime


class ProjectSectionRead(BaseModel):
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
    entries: list[ProjectEntryRead] = []


class ProjectSectionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=PROJECT_TITLE_MAX_LEN)
    organisation: str | None = Field(default=None, min_length=1, max_length=PROJECT_ORGANISATION_MAX_LEN)
    start_date: str | None = Field(default=None, min_length=1, max_length=PROJECT_DATE_MAX_LEN)
    end_date: str | None = Field(default=None, min_length=1, max_length=PROJECT_DATE_MAX_LEN)
    is_enabled: bool | None = None
    display_order: int | None = Field(default=None, ge=0)

    @field_validator("title")
    @classmethod
    def title_must_not_be_null(cls, v: str | None) -> str:
        if v is None:
            raise ValueError("title cannot be set to null")
        return v


class ProjectEntryCreate(BaseModel):
    content: str = Field(min_length=1, max_length=PROJECT_ENTRY_CONTENT_MAX_LEN)
    display_order: int = Field(default=0, ge=0)


class ProjectEntryUpdate(BaseModel):
    content: str | None = Field(
        default=None, min_length=1, max_length=PROJECT_ENTRY_CONTENT_MAX_LEN
    )
    display_order: int | None = Field(default=None, ge=0)
