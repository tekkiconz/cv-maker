from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status

from app.apis.dependencies import get_project_section_service
from app.exceptions import EntryLimitExceededError, SectionLimitExceededError
from app.schemas.sections.projects import (
    ProjectEntryCreate,
    ProjectEntryRead,
    ProjectEntryUpdate,
    ProjectSectionCreate,
    ProjectSectionRead,
    ProjectSectionUpdate,
)
from app.services.sections.projects_service import ProjectSectionService

router = APIRouter(
    prefix="/api/profiles/{profile_id}/sections/projects",
    tags=["projects"],
)

ProfileId = Annotated[int, Path(ge=1)]
SectionId = Annotated[int, Path(ge=1)]
EntryId = Annotated[int, Path(ge=1)]
ServiceDep = Annotated[ProjectSectionService, Depends(get_project_section_service)]


@router.post("", response_model=ProjectSectionRead, status_code=status.HTTP_201_CREATED)
async def create_project_section(
    profile_id: ProfileId,
    data: ProjectSectionCreate,
    service: ServiceDep,
) -> ProjectSectionRead:
    try:
        return await service.create_project_section(profile_id, data)
    except SectionLimitExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from None
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        ) from None


@router.get("", response_model=list[ProjectSectionRead])
async def list_project_sections(
    profile_id: ProfileId,
    service: ServiceDep,
) -> list[ProjectSectionRead]:
    try:
        return await service.list_project_sections(profile_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        ) from None


@router.get("/{section_id}", response_model=ProjectSectionRead)
async def get_project_section(
    profile_id: ProfileId,
    section_id: SectionId,
    service: ServiceDep,
) -> ProjectSectionRead:
    try:
        return await service.get_project_section(profile_id, section_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Section not found"
        ) from None


@router.patch("/{section_id}", response_model=ProjectSectionRead)
async def update_project_section(
    profile_id: ProfileId,
    section_id: SectionId,
    data: ProjectSectionUpdate,
    service: ServiceDep,
) -> ProjectSectionRead:
    try:
        return await service.update_project_section(profile_id, section_id, data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Section not found"
        ) from None


@router.delete("/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_section(
    profile_id: ProfileId,
    section_id: SectionId,
    service: ServiceDep,
) -> Response:
    try:
        await service.delete_project_section(profile_id, section_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Section not found"
        ) from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{section_id}/entries",
    response_model=ProjectEntryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_entry(
    profile_id: ProfileId,
    section_id: SectionId,
    data: ProjectEntryCreate,
    service: ServiceDep,
) -> ProjectEntryRead:
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


@router.patch("/{section_id}/entries/{entry_id}", response_model=ProjectEntryRead)
async def update_entry(
    profile_id: ProfileId,
    section_id: SectionId,
    entry_id: EntryId,
    data: ProjectEntryUpdate,
    service: ServiceDep,
) -> ProjectEntryRead:
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
