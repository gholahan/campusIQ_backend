from fastapi import APIRouter, Depends

from app.features.users.models import User
from app.db.session import SessionDep
from app.features.auth.dependencies import require_tutor
from app.features.tutors.schema import (
    TutorProfileCreate,
    TutorProfileRead,
    TutorProfileUpdate,
)
from app.features.tutors.service import (
    create_tutor_profile_service,
    get_tutor_profile_response,
    update_tutor_profile_service,
)

router = APIRouter(prefix="/tutors", tags=["Tutors"])


@router.post("/profile", response_model=TutorProfileRead)
async def create_tutor_profile(
    payload: TutorProfileCreate,
    session: SessionDep,
    auth_user: User = Depends(require_tutor),
):
    return await create_tutor_profile_service(   # ← was missing await
        session=session,
        auth_user=auth_user,
        payload=payload,
    )


@router.get("/profile", response_model=TutorProfileRead)
async def get_tutor_profile(
    session: SessionDep,
    auth_user: User = Depends(require_tutor),
):
    return await get_tutor_profile_response(
        session=session,
        user_id=auth_user.id,
    )


@router.patch("/profile", response_model=TutorProfileRead)  # ← was missing response_model
async def update_tutor_profile(
    payload: TutorProfileUpdate,
    session: SessionDep,
    auth_user: User = Depends(require_tutor),
):
    return await update_tutor_profile_service(
        session=session,
        auth_user=auth_user,
        payload=payload,
    )