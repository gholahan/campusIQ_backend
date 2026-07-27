import uuid
from fastapi import APIRouter, Depends
from app.db.session import SessionDep
from app.features.auth.dependencies import require_student, require_tutor, get_current_user 
from app.features.users.models import User
from app.features.sessions import service
from app.features.sessions.schema import (
    SessionCreate, PostSessionResponse, SessionRead, 
    SessionParams, AcceptSession, ReviewCreate, ReviewRead
)

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("/", response_model=PostSessionResponse, status_code=201)
async def create_session(
    data: SessionCreate,
    db: SessionDep,
    current_user: User = Depends(require_student),
):
    return await service.create_session(current_user.id, data, db)

@router.get("/student", response_model=list[SessionRead])
async def list_student_sessions(
    db: SessionDep,
    current_user: User = Depends(require_student),
    params: SessionParams = Depends(),
):
    return await service.get_student_sessions(
        db,
        current_user.id,
        params,
    )

@router.get("/tutor", response_model=list[SessionRead])
async def list_tutor_sessions(
    db: SessionDep,
    current_user: User = Depends(require_tutor),
    params: SessionParams = Depends(),
):
    return await service.get_tutor_sessions(
        db,
        current_user.id,
        params,
    )

@router.get("/{session_id}", response_model=SessionRead)
async def get_session(
    session_id: uuid.UUID,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    return await service.get_session(session_id, current_user.id, db)


@router.patch("/{session_id}/accept")
async def accept_session(
    session_id: uuid.UUID,
    data: AcceptSession,
    db: SessionDep,
    current_user: User = Depends(require_tutor),
):
    return await service.accept_session(session_id, current_user.id, data, db)


@router.patch("/{session_id}/decline")
async def decline_session(
    session_id: uuid.UUID,
    db: SessionDep,
    current_user: User = Depends(require_tutor),
):
    return await service.decline_session(session_id, current_user.id, db)


@router.patch("/{session_id}/cancel")
async def cancel_session(
    session_id: uuid.UUID,
    db: SessionDep,
    current_user: User = Depends(require_student),
):
    return await service.cancel_session(session_id, current_user.id, db)


@router.patch("/{session_id}/start")
async def start_session(
    session_id: uuid.UUID,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    return await service.start_session(session_id, current_user.id, db)


@router.patch("/{session_id}/end")
async def end_session(
    session_id: uuid.UUID,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    return await service.end_session(session_id, current_user.id, db)


@router.post("/{session_id}/review", response_model=ReviewRead, status_code=201)
async def submit_review(
    session_id: uuid.UUID,
    data: ReviewCreate,
    db: SessionDep,
    current_user: User = Depends(require_student),
):
    return await service.submit_review(session_id, current_user.id, data, db)


@router.get("/{session_id}/review", response_model=ReviewRead)
async def get_review(
    session_id: uuid.UUID,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    return await service.get_review(session_id, db)