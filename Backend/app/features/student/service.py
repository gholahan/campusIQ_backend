import uuid

from app.db.session import SessionDep
from app.features.student.schema import (
    StudentStatsResponse,
    SessionsStats,
    LearningStats,
    TutorsStats,
    AIStats,
)

from app.features.sessions.service import (
    get_student_this_week_session_count,
    get_student_last_week_session_count,
    get_student_weekly_completed_hours,
    get_student_active_tutors_this_week,
)


async def get_student_dashboard_stats_service(
    db: SessionDep,
    student_id: uuid.UUID,
) -> StudentStatsResponse:

    this_week_sessions = await get_student_this_week_session_count(
        db,
        student_id,
    )

    last_week_sessions = await get_student_last_week_session_count(
        db,
        student_id,
    )

    completed_hours = await get_student_weekly_completed_hours(
        db,
        student_id,
    )

    active_tutors = await get_student_active_tutors_this_week(
        db,
        student_id,
    )

    return StudentStatsResponse(
        sessions=SessionsStats(
            this_week=this_week_sessions,
            delta=this_week_sessions-last_week_sessions,
        ),
        learning=LearningStats(
            hours_this_week=completed_hours,
        ),
        tutors=TutorsStats(
            active_this_week=active_tutors,
        ),
        ai=AIStats(
            questions_this_week=0,  # placeholder until AI tracking exists
        ),
    )