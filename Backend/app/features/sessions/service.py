import uuid
from fastapi import HTTPException
from sqlmodel import desc, select
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from app.common.enums import SessionStatus
from app.db.session import SessionDep
from app.features.tutors.models import Course, TutorCourse, TutorProfile
from app.features.sessions.models import Session
from app.features.sessions.schema import (
    ScheduledAt, SessionCreate, SessionRead, SessionTutorRead,
    SessionParams, AcceptSession, ReviewCreate, ReviewRead
)
from app.features.reviews.models import Review


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
    student_id: uuid.UUID,
    params: SessionParams,
) -> list[SessionRead]:
    query = (
        select(Session, TutorProfile)
        .join(TutorProfile, TutorProfile.user_id == Session.tutor_id)
        .where(Session.student_id == student_id)
    )

    if params.status is not None:
        query = query.where(Session.status == params.status)

    query = query.order_by(desc(Session.created_at))

    result = await db.exec(query)
    sessions = result.all()

    return [
        SessionRead(
            id=session.id,
            subject=session.subject,
            duration=session.duration,
            notes=session.notes,
            status=session.status,
            cost=session.cost,
            meet_link=session.meet_link,      
            started_at=session.started_at,    
            ended_at=session.ended_at,
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

async def get_student_this_week_session_count(
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

async def get_student_last_week_session_count(
    db: SessionDep,
    student_id: uuid.UUID
) -> int:
    now = datetime.now(timezone.utc)

    # Start of this week (Monday 00:00 UTC)
    start_of_this_week = (
        now - timedelta(days=now.weekday())
    ).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    # Start and end of last week
    start_of_last_week = start_of_this_week - timedelta(days=7)
    end_of_last_week = start_of_this_week - timedelta(seconds=1)

    result = await db.exec(
        select(func.count(Session.id)).where(
            Session.student_id == student_id,
            Session.created_at >= start_of_last_week,
            Session.created_at <= end_of_last_week,
        )
    )

    return result.one()


async def get_student_weekly_completed_hours(
    db: SessionDep,
    student_id: uuid.UUID,
) -> float:
    now = datetime.now(timezone.utc)

    start_of_week = (
        now - timedelta(days=now.weekday())
    ).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    result = await db.exec(
        select(func.sum(Session.duration))
        .where(
            Session.student_id == student_id,
            Session.status == SessionStatus.completed,
            Session.created_at >= start_of_week,
        )
    )

    return float(result.one() or 0)


async def get_student_active_tutors_this_week(
    db: SessionDep,
    student_id: uuid.UUID,
) -> int:
    now = datetime.now(timezone.utc)

    start_of_week = (
        now - timedelta(days=now.weekday())
    ).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    result = await db.exec(
        select(func.count(func.distinct(Session.tutor_id)))
        .where(
            Session.student_id == student_id,
            Session.created_at >= start_of_week,
        )
    )

    return result.one()


async def get_tutor_sessions(
    db: SessionDep,
    tutor_id: uuid.UUID,
    params: SessionParams,
):
    query = (
        select(Session, TutorProfile)
        .join(TutorProfile, TutorProfile.user_id == Session.tutor_id)
        .where(Session.tutor_id == tutor_id)
    )

    if params.status is not None:
        query = query.where(Session.status == params.status)

    query = query.order_by(desc(Session.created_at))

    result = await db.exec(query)
    sessions = result.all()

    return [
        SessionRead(
            id=session.id,
            subject=session.subject,
            duration=session.duration,
            notes=session.notes,
            status=session.status,
            cost=session.cost,
            meet_link=session.meet_link,
            started_at=session.started_at, 
            ended_at=session.ended_at,        
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

async def get_session(
    session_id: uuid.UUID,
    user_id: uuid.UUID,
    db: SessionDep,
) -> SessionRead:
    result = await db.exec(
        select(Session, TutorProfile)
        .join(TutorProfile, TutorProfile.user_id == Session.tutor_id)
        .where(Session.id == session_id)
    )
    row = result.first()

    if not row:
        raise HTTPException(404, "Session not found")

    session, tutor = row

    if user_id not in (session.student_id, session.tutor_id):
        raise HTTPException(403, "Not part of this session")

    return SessionRead(
        id=session.id,
        subject=session.subject,
        duration=session.duration,
        notes=session.notes,
        status=session.status,
        cost=session.cost,
        meet_link=session.meet_link,
        started_at=session.started_at,
        ended_at=session.ended_at,
        tutor=SessionTutorRead(
            id=tutor.user_id,
            full_name=tutor.full_name,
            profile_picture_url=tutor.profile_picture_url,
        ),
        scheduled_at=ScheduledAt(**session.scheduled_at),
        created_at=session.created_at,
    )


async def accept_session(
    session_id: uuid.UUID,
    tutor_id: uuid.UUID,
    data: AcceptSession,
    db: SessionDep,
) -> Session:
    session = await db.get(Session, session_id)

    if not session:
        raise HTTPException(404, "Session not found")
    if session.tutor_id != tutor_id:
        raise HTTPException(403, "Not your session")
    if session.status != SessionStatus.pending:
        raise HTTPException(400, f"Cannot accept a session with status '{session.status}'")

    session.status = SessionStatus.accepted
    session.meet_link = data.meet_link

    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def decline_session(
    session_id: uuid.UUID,
    tutor_id: uuid.UUID,
    db: SessionDep,
) -> Session:
    session = await db.get(Session, session_id)

    if not session:
        raise HTTPException(404, "Session not found")
    if session.tutor_id != tutor_id:
        raise HTTPException(403, "Not your session")
    if session.status not in (SessionStatus.pending, SessionStatus.accepted):
        raise HTTPException(400, f"Cannot decline a session with status '{session.status}'")

    session.status = SessionStatus.declined

    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def cancel_session(
    session_id: uuid.UUID,
    student_id: uuid.UUID,
    db: SessionDep,
) -> Session:
    session = await db.get(Session, session_id)

    if not session:
        raise HTTPException(404, "Session not found")
    if session.student_id != student_id:
        raise HTTPException(403, "Not your session")
    if session.status not in (SessionStatus.pending, SessionStatus.accepted):
        raise HTTPException(400, f"Cannot cancel a session with status '{session.status}'")

    session.status = SessionStatus.cancelled

    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def start_session(
    session_id: uuid.UUID,
    user_id: uuid.UUID,
    db: SessionDep,
) -> Session:
    session = await db.get(Session, session_id)

    if not session:
        raise HTTPException(404, "Session not found")
    if user_id not in (session.student_id, session.tutor_id):
        raise HTTPException(403, "Not part of this session")
    if session.status != SessionStatus.accepted:
        raise HTTPException(400, f"Cannot start a session with status '{session.status}'")

    session.status = SessionStatus.in_progress
    session.started_at = datetime.now(timezone.utc)

    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def end_session(
    session_id: uuid.UUID,
    user_id: uuid.UUID,
    db: SessionDep,
) -> Session:
    session = await db.get(Session, session_id)

    if not session:
        raise HTTPException(404, "Session not found")
    if user_id not in (session.student_id, session.tutor_id):
        raise HTTPException(403, "Not part of this session")
    if session.status != SessionStatus.in_progress:
        raise HTTPException(400, f"Cannot end a session with status '{session.status}'")

    now = datetime.now(timezone.utc)
    session.status = SessionStatus.completed
    session.ended_at = now

    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def submit_review(
    session_id: uuid.UUID,
    student_id: uuid.UUID,
    data: ReviewCreate,
    db: SessionDep,
) -> Review:
    session = await db.get(Session, session_id)

    if not session:
        raise HTTPException(404, "Session not found")
    if session.student_id != student_id:
        raise HTTPException(403, "Not your session")
    if session.status != SessionStatus.completed:
        raise HTTPException(400, "Can only review completed sessions")

    existing = await db.exec(
        select(Review).where(Review.session_id == session_id)
    )
    if existing.first():
        raise HTTPException(400, "Session already reviewed")

    review = Review(
        session_id=session_id,
        student_id=student_id,
        tutor_id=session.tutor_id,
        rating=data.rating,
        comment=data.comment,
    )

    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review


async def get_review(
    session_id: uuid.UUID,
    db: SessionDep,
) -> Review:
    result = await db.exec(
        select(Review).where(Review.session_id == session_id)
    )
    review = result.first()

    if not review:
        raise HTTPException(404, "No review for this session")

    return review