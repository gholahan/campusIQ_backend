import uuid
from sqlmodel import select
from sqlalchemy import func
from datetime import datetime, timezone, timedelta

from app.db.session import SessionDep
from app.features.student.schema import (
    StudentStatsResponse,
    SessionsStats,
    LearningStats,
    TutorsStats,
    AIStats,
)
from app.features.ai.models import AIMessage, AIConversation
from app.common.enums import AiChatRole

from app.features.sessions.service import (
    get_student_this_week_session_count,
    get_student_last_week_session_count,
    get_student_weekly_completed_hours,
    get_student_active_tutors_this_week,
)

async def get_student_ai_questions_this_week_service(
    db: SessionDep,
    student_id: uuid.UUID,
) -> int:
    now = datetime.now(timezone.utc)

    start_of_week = (now - timedelta(days=now.weekday())).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    result = await db.exec(  # type: ignore[arg-type]
        select(func.count(AIMessage.id))
        .join(AIConversation, AIConversation.id == AIMessage.conversation_id)
        .where(
            AIConversation.user_id == student_id,
            AIMessage.role == AiChatRole.user,
            AIMessage.created_at >= start_of_week,
        )
)

    return int(result.one() or 0)


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
    ai_questions_this_week = await get_student_ai_questions_this_week_service(
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
            questions_this_week=ai_questions_this_week,
        ),
    )