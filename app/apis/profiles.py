from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.apis.dependencies import get_profile_service
from app.schemas.profile import ProfileCreate, ProfileRead
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


@router.post("", response_model=ProfileRead, status_code=status.HTTP_201_CREATED)
async def create_profile(
    data: ProfileCreate,
    service: Annotated[ProfileService, Depends(get_profile_service)],
) -> ProfileRead:
    return await service.create_profile(data)


@router.get("", response_model=list[ProfileRead])
async def list_profiles(
    service: Annotated[ProfileService, Depends(get_profile_service)],
) -> list[ProfileRead]:
    return await service.list_profiles()
