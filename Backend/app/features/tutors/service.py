from decimal import Decimal
from datetime import time
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import select

from app.db.session import SessionDep
from app.features.courses.schema import CourseRead
from app.features.courses.services import get_or_create_course
from app.features.tutors.models import Course, TutorCourse, TutorProfile
from app.features.tutors.schema import (
    TutorProfileCreate,
    TutorProfileRead,
    TutorProfileUpdate,
    TutorSearchParams,
    TutorSearchResult,
)
from app.features.users.models import User


# ----------------------------
# Availability Serializer
# ----------------------------
def serialize_availability(availability: dict | None):
    if not availability:
        return None

    serialized = {}

    for day, slot in availability.items():
        day_key = str(getattr(day, "value", day))

        start = slot.get("start")
        end = slot.get("end")

        serialized[day_key] = {
            "start": (
                start.strftime("%H:%M")
                if isinstance(start, time)
                else str(start)
            ),
            "end": (
                end.strftime("%H:%M")
                if isinstance(end, time)
                else str(end)
            ),
        }

    return serialized


# ----------------------------
# CREATE
# ----------------------------
async def create_tutor_profile_service(
    session: SessionDep,
    auth_user: User,
    payload: TutorProfileCreate,
):
    existing = await session.get(TutorProfile, auth_user.id)

    if existing:
        raise HTTPException(status_code=409, detail="Profile already exists")

    availability = serialize_availability(
        {k.value: v.model_dump() for k, v in payload.availability.items()}
    )

    tutor = TutorProfile(
        user_id=auth_user.id,
        full_name=payload.name,
        title=payload.title,
        bio=payload.bio,
        hourly_rate=Decimal(str(payload.hourly_rate)),
        availability=availability,
        is_online=True,
    )

    session.add(tutor)
    await session.flush()

    await _merge_tutor_courses(session, auth_user.id, payload.courses)

    await session.commit()

    return await get_tutor_profile_response(session, auth_user.id)


# ----------------------------
# RESPONSE
# ----------------------------
async def get_tutor_profile_response(
    session: SessionDep,
    user_id: UUID,
) -> TutorProfileRead:
    tutor = await session.get(TutorProfile, user_id)

    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor profile not found")

    statement = (
        select(Course)
        .join(TutorCourse, TutorCourse.course_id == Course.id)
        .where(TutorCourse.tutor_id == user_id)
    )

    result = await session.exec(statement)
    courses = result.all()

    return TutorProfileRead(
        user_id=tutor.user_id,
        full_name=tutor.full_name,
        title=tutor.title,
        bio=tutor.bio,
        hourly_rate=tutor.hourly_rate,
        availability=tutor.availability,
        is_online=tutor.is_online,
        average_rating=tutor.average_rating,
        review_count=tutor.review_count,
        total_sessions=tutor.total_sessions,
        courses=[CourseRead(id=c.id, name=c.name) for c in courses],
    )


# ----------------------------
# COURSES MERGE
# ----------------------------
async def _merge_tutor_courses(
    session: SessionDep,
    tutor_id: UUID,
    new_courses: list[str] | None,
):
    if not new_courses:
        return

    existing = await session.exec(
        select(Course)
        .join(TutorCourse, TutorCourse.course_id == Course.id) #type: ignore
        .where(TutorCourse.tutor_id == tutor_id)
    )

    existing_names = {c.name.lower() for c in existing.all()}

    for name in new_courses:
        if name.lower() in existing_names:
            continue

        course = await get_or_create_course(session, name)

        session.add(
            TutorCourse(
                tutor_id=tutor_id,
                course_id=course.id
            )
        )


# ----------------------------
# UPDATE (TRUE MERGE PATCH)
# ----------------------------
async def update_tutor_profile_service(
    session: SessionDep,
    auth_user: User,
    payload: TutorProfileUpdate,
):
    tutor = await session.get(TutorProfile, auth_user.id)

    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor profile not found")

    update_data = payload.model_dump(exclude_unset=True)

    # name mapping
    if "name" in update_data:
        tutor.full_name = update_data.pop("name")

    new_courses = update_data.pop("courses", None)

    # availability merge (true patch)
    if "availability" in update_data:
        incoming = update_data.pop("availability") or {}

        incoming_serialized = serialize_availability(incoming)
        current = tutor.availability or {}

        merged = dict(current)

        for day, slot in incoming_serialized.items():
            merged[day] = slot   # ONLY override specific day

        update_data["availability"] = merged

    # scalar updates
    for key, value in update_data.items():
        setattr(tutor, key, value)

    # merge courses (no replace)
    await _merge_tutor_courses(session, auth_user.id, new_courses)

    session.add(tutor)
    await session.commit()

    return await get_tutor_profile_response(
        session,
        auth_user.id,
    )


# ----------------------------
# SEARCH(Tutor)
# ----------------------------
async def search_tutors_service(
    session: SessionDep,
    params: TutorSearchParams
) -> TutorSearchResult:

    from sqlalchemy import (
        func as sa_func,
        asc,
        desc,
        or_,
        and_,
    )
    from sqlalchemy.orm import selectinload

    stmt = (
        select(TutorProfile)
        .options(selectinload(TutorProfile.courses))
    )

    joined_course = False

    # -------------------------
    # BASIC FILTERS
    # -------------------------

    if params.is_online is not None:
        stmt = stmt.where(
            TutorProfile.is_online == params.is_online
        )

    if params.min_rate is not None:
        stmt = stmt.where(
            TutorProfile.hourly_rate >= params.min_rate
        )

    if params.max_rate is not None:
        stmt = stmt.where(
            TutorProfile.hourly_rate <= params.max_rate
        )

    if params.min_rating is not None:
        stmt = stmt.where(
            TutorProfile.average_rating >= params.min_rating
        )

    # -------------------------
    # NAME FILTER
    # -------------------------

    if params.name:
        stmt = stmt.where(
            TutorProfile.full_name.ilike(f"%{params.name}%")
        )

    # -------------------------
    # COURSE FILTER
    # -------------------------

    if params.course:
        term = params.course.strip()
        similarity_col = sa_func.max(sa_func.similarity(Course.name, term)).label("course_sim")
        stmt = (
            stmt
            .join(
                TutorCourse,
                TutorCourse.tutor_id == TutorProfile.user_id
            )
            .join(
                Course,
                Course.id == TutorCourse.course_id
            )
            .where(
                Course.name.ilike(f"%{params.course}%")
            )
        )

        joined_course = True

    # -------------------------
    # GLOBAL SEARCH
    # -------------------------

    if params.q:

        if not joined_course:
            stmt = (
                stmt
                .join(
                    TutorCourse,
                    TutorCourse.tutor_id == TutorProfile.user_id
                )
                .join(
                    Course,
                    Course.id == TutorCourse.course_id
                )
            )

        terms = params.q.lower().split()

        conditions = []

        for term in terms:
            conditions.append(
                or_(
                    TutorProfile.full_name.ilike(f"%{term}%"),
                    TutorProfile.title.ilike(f"%{term}%"),
                    Course.name.ilike(f"%{term}%"),

                    sa_func.similarity(
                        TutorProfile.full_name,
                        term
                    ) > 0.3,

                    sa_func.similarity(
                        Course.name,
                        term
                    ) > 0.3,
                )
            )

        stmt = stmt.where(and_(*conditions))

    # -------------------------
    # REMOVE DUPLICATES
    # -------------------------

    stmt = stmt.group_by(TutorProfile.user_id)

    # -------------------------
    # COUNT
    # -------------------------

    count_stmt = select(
        sa_func.count()
    ).select_from(
        stmt.with_only_columns(
            TutorProfile.user_id
        ).subquery()
    )

    total = (await session.exec(count_stmt)).one()

    # -------------------------
    # ORDERING
    # -------------------------

    if params.q:
        stmt = stmt.order_by(
            desc(TutorProfile.average_rating)
        )

    else:
        order_col = (
            TutorProfile.hourly_rate
            if params.order_by == "hourly_rate"
            else TutorProfile.average_rating
        )

        stmt = stmt.order_by(
            asc(order_col)
            if params.order_dir == "asc"
            else desc(order_col)
        )

    # -------------------------
    # PAGINATION
    # -------------------------

    stmt = (
        stmt
        .offset(params.offset)
        .limit(params.limit)
    )

    result = await session.exec(stmt)
    tutors = result.unique().all()

    # -------------------------
    # RESPONSE
    # -------------------------

    return TutorSearchResult(
        total=total,
        tutors=[
            TutorProfileRead(
                user_id=t.user_id,
                full_name=t.full_name,
                title=t.title,
                bio=t.bio,
                hourly_rate=t.hourly_rate,
                availability=t.availability,
                is_online=t.is_online,
                average_rating=t.average_rating,
                review_count=t.review_count,
                total_sessions=t.total_sessions,
                courses=[
                    CourseRead(
                        id=c.id,
                        name=c.name
                    )
                    for c in t.courses
                ],
            )
            for t in tutors
        ],
    )