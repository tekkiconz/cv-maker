from fastapi import APIRouter

from app.apis.sections.education import router as education_router
from app.apis.sections.experience import router as experience_router

sections_router = APIRouter()
sections_router.include_router(experience_router)
sections_router.include_router(education_router)
