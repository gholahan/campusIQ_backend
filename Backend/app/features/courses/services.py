from sqlmodel import select

from app.db.session import SessionDep
from app.features.tutors.models import Course


async def get_or_create_course(session: SessionDep, name: str):
    normalized = name.strip().lower()

    result = await session.exec(
        select(Course).where(Course.name == normalized)
    )
    course = result.first()

    if course:
        return course

    course = Course(name=normalized)
    session.add(course)
    await session.flush()  # gets ID without commit
    return course