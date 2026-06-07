import uuid
from fastapi import HTTPException
from sqlmodel import desc, select
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from app.db.session import SessionDep
from app.features.tutors.models import Course, TutorCourse, TutorProfile
from app.features.sessions.models import Session
from app.features.sessions.schema import ScheduledAt, SessionCreate, SessionRead, SessionTutorRead

async def create_session(
    student_id: uuid.UUID,
    data: SessionCreate,
    db: SessionDep
) -> Session:

    # 1. Validate tutor exists
    tutor = await db.get(TutorProfile, data.tutor_id)
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor profile does not exist")

    # 2. Validate subject belongs to tutor

    result = await db.exec(
        select(Course).join(TutorCourse, TutorCourse.course_id == Course.id)
        .where(TutorCourse.tutor_id == data.tutor_id)
    )

    tutor_courses = [c.name for c in result.all()]

    if data.subject not in tutor_courses:
        raise HTTPException(
            status_code=400,
            detail="Tutor does not handle this course"
        )

    # 3. Calculate cost server-side (IMPORTANT)
    if tutor.hourly_rate is None:
        raise HTTPException(
            status_code=400,
            detail="Tutor hourly rate not set"
        )

    cost = float(tutor.hourly_rate) * float(data.duration)

    # 4. Create session AFTER validation
    new_session = Session(
        student_id=student_id,
        tutor_id=data.tutor_id,
        subject=data.subject,
        duration=data.duration,
        scheduled_at=data.scheduled_at.model_dump(),
        notes=data.notes,
        cost=cost
    )

    # 5. Save
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    return new_session


async def get_student_sessions(
    db: SessionDep,
    student_id: uuid.UUID
) -> list[SessionRead]:
    result = await db.exec(
        select(Session, TutorProfile)
        .join(TutorProfile, TutorProfile.user_id == Session.tutor_id)
        .where(Session.student_id == student_id)
        .order_by(desc(Session.created_at))
    )
    sessions = result.all()

    return [
        SessionRead(
            id=session.id,
            subject=session.subject,
            duration=session.duration,
            notes=session.notes,
            status=session.status,
            cost=session.cost,
            tutor=SessionTutorRead(
                id=tutor.user_id,
                full_name=tutor.full_name,
                profile_picture_url=tutor.profile_picture_url,
            ),
            scheduled_at=ScheduledAt(**session.scheduled_at),
            created_at=session.created_at,
        )
        for session, tutor in sessions
    ]


async def get_student_session_count(
    db: SessionDep,
    student_id: uuid.UUID,
) -> int:
    result = await db.exec(
        select(func.count(Session.id)).where(
            Session.student_id == student_id
        )
    )

    return result.one()

async def get_student_weekly_session_count(
    db: SessionDep,
    student_id: uuid.UUID
) -> int:
    now = datetime.now(timezone.utc)

    # Monday 00:00:00 of the current week
    start_of_week = (now - timedelta(days=now.weekday())).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    result = await db.exec(
        select(func.count(Session.id)).where(
            Session.student_id == student_id,
            Session.created_at >= start_of_week,
        )
    )

    return result.one()
