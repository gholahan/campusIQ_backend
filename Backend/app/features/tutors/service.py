# app/features/tutors/service.py

from decimal import Decimal
from typing import Any

from sqlmodel import select

from app.db.session import SessionDep
from app.features.users.models import User
from app.features.tutors.models import TutorProfile


async def sync_tutor_profile_service(
    session: SessionDep,
    auth_user: Any,
    payload: dict[str, Any],
) -> TutorProfile:

    user_id = auth_user.id

    # --------------------------
    # ensure user exists
    # --------------------------
    user = await session.get(User, user_id)

    if not user:
        raise ValueError("User does not exist")

    # --------------------------
    # check existing tutor profile
    # --------------------------
    statement = select(TutorProfile).where(
        TutorProfile.user_id == user_id
    )

    result = await session.exec(statement)

    existing = result.first()

    # --------------------------
    # normalize payload
    # --------------------------
    courses: list[str] = payload.get("courses") or []

    if isinstance(courses, str):
        courses = [c.strip() for c in courses.split(",")]

    hourly_rate = payload.get("hourlyRate")

    if hourly_rate is not None:
        hourly_rate = Decimal(str(hourly_rate))

    # --------------------------
    # update or create
    # --------------------------
    if existing:
        existing.bio = payload.get("bio", existing.bio)
        existing.courses = courses or existing.courses
        existing.hourly_rate = hourly_rate or existing.hourly_rate

        session.add(existing)
        await session.commit()
        await session.refresh(existing)
        return existing

    tutor = TutorProfile(
        user_id=user_id,
        bio=payload.get("bio"),
        courses=courses,
        hourly_rate=hourly_rate,
    )

    session.add(tutor)
    await session.commit()
    await session.refresh(tutor)

    return tutor