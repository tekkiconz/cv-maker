from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.constants.limits import PROFILE_DESCRIPTION_MAX_LEN, PROFILE_NAME_MAX_LEN

ProfileName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=PROFILE_NAME_MAX_LEN),
]


class ProfileCreate(BaseModel):
    name: ProfileName
    description: str | None = Field(None, max_length=PROFILE_DESCRIPTION_MAX_LEN)


class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


ProfileList = list[ProfileRead]


class ProfileUpdate(BaseModel):
    name: ProfileName | None = None
    description: str | None = Field(default=None, max_length=PROFILE_DESCRIPTION_MAX_LEN)
