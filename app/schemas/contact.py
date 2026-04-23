from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from app.constants.enums import ContactType

ContactValue = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=500),
]


class ContactCreate(BaseModel):
    type: ContactType
    value: ContactValue


class ContactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profile_id: int
    type: ContactType
    value: str


class ContactUpdate(BaseModel):
    value: ContactValue | None = None
