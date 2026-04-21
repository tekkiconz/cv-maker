from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants.limits import PROFILE_DESCRIPTION_MAX_LEN, PROFILE_NAME_MAX_LEN


class ProfileCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=PROFILE_NAME_MAX_LEN)
    description: str | None = Field(None, max_length=PROFILE_DESCRIPTION_MAX_LEN)

    @field_validator("name", mode="before")
    @classmethod
    def strip_and_validate_name(cls, v: str) -> str:
        if isinstance(v, str):
            stripped = v.strip()
            if not stripped:
                raise ValueError("name cannot be whitespace-only")
            return stripped
        return v


class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


ProfileList = list[ProfileRead]
