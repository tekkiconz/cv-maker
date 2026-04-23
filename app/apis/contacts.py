from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status

from app.apis.dependencies import get_contact_service
from app.schemas.contact import ContactCreate, ContactRead, ContactUpdate
from app.services.contact_service import ContactService

router = APIRouter(prefix="/api/profiles/{profile_id}/contacts", tags=["contacts"])


@router.post("", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
async def create_contact(
    profile_id: Annotated[int, Path(ge=1)],
    data: ContactCreate,
    service: Annotated[ContactService, Depends(get_contact_service)],
) -> ContactRead:
    try:
        return await service.create_contact(profile_id, data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        ) from None


@router.get("", response_model=list[ContactRead])
async def list_contacts(
    profile_id: Annotated[int, Path(ge=1)],
    service: Annotated[ContactService, Depends(get_contact_service)],
) -> list[ContactRead]:
    try:
        return await service.list_contacts(profile_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        ) from None


@router.patch("/{contact_id}", response_model=ContactRead)
async def update_contact(
    profile_id: Annotated[int, Path(ge=1)],
    contact_id: Annotated[int, Path(ge=1)],
    data: ContactUpdate,
    service: Annotated[ContactService, Depends(get_contact_service)],
) -> ContactRead:
    try:
        return await service.update_contact(profile_id, contact_id, data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        ) from None


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    profile_id: Annotated[int, Path(ge=1)],
    contact_id: Annotated[int, Path(ge=1)],
    service: Annotated[ContactService, Depends(get_contact_service)],
) -> Response:
    try:
        await service.delete_contact(profile_id, contact_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        ) from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)
