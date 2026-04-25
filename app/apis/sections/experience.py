from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status

from app.apis.dependencies import get_experience_section_service
from app.exceptions import EntryLimitExceededError, SectionLimitExceededError
from app.schemas.sections.experience import (
    ExperienceEntryCreate,
    ExperienceEntryRead,
    ExperienceEntryUpdate,
    ExperienceSectionCreate,
    ExperienceSectionRead,
    ExperienceSectionUpdate,
)
from app.services.sections.experience_service import ExperienceSectionService

router = APIRouter(
    prefix="/api/profiles/{profile_id}/sections/experience",
    tags=["experience"],
)

ProfileId = Annotated[int, Path(ge=1)]
SectionId = Annotated[int, Path(ge=1)]
EntryId = Annotated[int, Path(ge=1)]
ServiceDep = Annotated[ExperienceSectionService, Depends(get_experience_section_service)]


@router.post("", response_model=ExperienceSectionRead, status_code=status.HTTP_201_CREATED)
async def create_experience_section(
    profile_id: ProfileId,
    data: ExperienceSectionCreate,
    service: ServiceDep,
) -> ExperienceSectionRead:
    try:
        return await service.create_experience_section(profile_id, data)
    except SectionLimitExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from None
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        ) from None


@router.get("", response_model=list[ExperienceSectionRead])
async def list_experience_sections(
    profile_id: ProfileId,
    service: ServiceDep,
) -> list[ExperienceSectionRead]:
    try:
        return await service.list_experience_sections(profile_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        ) from None


@router.get("/{section_id}", response_model=ExperienceSectionRead)
async def get_experience_section(
    profile_id: ProfileId,
    section_id: SectionId,
    service: ServiceDep,
) -> ExperienceSectionRead:
    try:
        return await service.get_experience_section(profile_id, section_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Section not found"
        ) from None


@router.patch("/{section_id}", response_model=ExperienceSectionRead)
async def update_experience_section(
    profile_id: ProfileId,
    section_id: SectionId,
    data: ExperienceSectionUpdate,
    service: ServiceDep,
) -> ExperienceSectionRead:
    try:
        return await service.update_experience_section(profile_id, section_id, data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Section not found"
        ) from None


@router.delete("/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experience_section(
    profile_id: ProfileId,
    section_id: SectionId,
    service: ServiceDep,
) -> Response:
    try:
        await service.delete_experience_section(profile_id, section_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Section not found"
        ) from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{section_id}/entries",
    response_model=ExperienceEntryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_entry(
    profile_id: ProfileId,
    section_id: SectionId,
    data: ExperienceEntryCreate,
    service: ServiceDep,
) -> ExperienceEntryRead:
    try:
        return await service.create_entry(profile_id, section_id, data)
    except EntryLimitExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from None
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Section not found"
        ) from None


@router.patch("/{section_id}/entries/{entry_id}", response_model=ExperienceEntryRead)
async def update_entry(
    profile_id: ProfileId,
    section_id: SectionId,
    entry_id: EntryId,
    data: ExperienceEntryUpdate,
    service: ServiceDep,
) -> ExperienceEntryRead:
    try:
        return await service.update_entry(profile_id, section_id, entry_id, data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found"
        ) from None


@router.delete("/{section_id}/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(
    profile_id: ProfileId,
    section_id: SectionId,
    entry_id: EntryId,
    service: ServiceDep,
) -> Response:
    try:
        await service.delete_entry(profile_id, section_id, entry_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found"
        ) from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)
