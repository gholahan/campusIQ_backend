import uuid

from fastapi import APIRouter, Depends
from app.features.student.schema import StudentStatsResponse
from app.features.auth.dependencies import require_student
from app.db.session import SessionDep
from app.features.student.service import get_student_dashboard_stats_service


router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/{student_id}/dashboard-stats",response_model=StudentStatsResponse)
async def get_student_dashboard_stats(student_id: uuid.UUID, db: SessionDep, auth_user: uuid.UUID = Depends(require_student)):
    return await get_student_dashboard_stats_service(db, student_id)
