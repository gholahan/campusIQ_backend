from fastapi import APIRouter, Depends
from app.db.session import SessionDep
from app.features.auth.dependencies import require_student
from app.features.users.models import User
from app.features.sessions.schema import SessionCreate, SessionResponse
from app.features.sessions import service

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("/", response_model=SessionResponse, status_code=201)
async def create_session(
    data: SessionCreate,
    db: SessionDep,
    current_user: User = Depends(require_student),
):
    return await service.create_session(current_user.id, data, db)


@router.get("/", response_model=list[SessionResponse])
async def list_sessions(
    db: SessionDep,
    current_user: User = Depends(require_student),
):
    return await service.get_student_sessions(db, current_user.id)


