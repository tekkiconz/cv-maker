from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.factories import make_sqlite_adapter, session_factory
from app.services.contact_service import ContactService
from app.services.profile_service import ProfileService
from app.services.sections.education_service import EducationSectionService
from app.services.sections.experience_service import ExperienceSectionService


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with session_factory() as session:
        yield session


async def get_profile_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ProfileService:
    adapter = make_sqlite_adapter(session)
    return ProfileService(adapter)


async def get_contact_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ContactService:
    adapter = make_sqlite_adapter(session)
    return ContactService(adapter)


async def get_experience_section_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ExperienceSectionService:
    adapter = make_sqlite_adapter(session)
    return ExperienceSectionService(adapter)


async def get_education_section_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EducationSectionService:
    adapter = make_sqlite_adapter(session)
    return EducationSectionService(adapter)
