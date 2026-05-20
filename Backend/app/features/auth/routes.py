from typing import Any
from fastapi import APIRouter, Depends
from sqlmodel import select
from app.features.tutors.models import TutorProfile
from app.db.session import SessionDep
from app.features.auth.dependencies import get_current_auth_user, get_current_user
from app.features.auth.schema import MeResponse, SyncUserRequest
from app.features.auth.services import sync_user_service
from app.features.users.models import User


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=MeResponse)
async def me(
    session: SessionDep,
    user: User = Depends(get_current_user),
) -> MeResponse:
    onboarding_complete = False

    if user.role == "tutor":
        result = await session.exec(
            select(TutorProfile).where(TutorProfile.user_id == user.id)
        )
        onboarding_complete = result.first() is not None

    return MeResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        onboarding_complete=onboarding_complete,
    )


@router.get("/profile", response_model=User)
async def get_profile(
    user: User = Depends(get_current_user),
) -> User:
    return user


@router.post("/sync-user", response_model=User)
async def sync_user(
    payload: SyncUserRequest,
    session: SessionDep,
    auth_user: Any = Depends(get_current_auth_user),
) -> User:
    return await sync_user_service(
        payload=payload,
        session=session,
        auth_user=auth_user,
    )