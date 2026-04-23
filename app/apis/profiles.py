from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.apis.dependencies import get_profile_service
from app.schemas.profile import ProfileCreate, ProfileList, ProfileRead, ProfileUpdate
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


@router.post("", response_model=ProfileRead, status_code=status.HTTP_201_CREATED)
async def create_profile(
    data: ProfileCreate,
    service: Annotated[ProfileService, Depends(get_profile_service)],
) -> ProfileRead:
    return await service.create_profile(data)


@router.get("", response_model=ProfileList)
async def list_profiles(
    service: Annotated[ProfileService, Depends(get_profile_service)],
) -> ProfileList:
    return await service.list_profiles()


@router.get("/{profile_id}", response_model=ProfileRead)
async def get_profile(
    profile_id: int,
    service: Annotated[ProfileService, Depends(get_profile_service)],
) -> ProfileRead:
    try:
        return await service.get_profile(profile_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        ) from None


@router.patch("/{profile_id}", response_model=ProfileRead)
async def update_profile(
    profile_id: int,
    data: ProfileUpdate,
    service: Annotated[ProfileService, Depends(get_profile_service)],
) -> ProfileRead:
    try:
        return await service.update_profile(profile_id, data)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        ) from None
