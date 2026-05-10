from typing import Any
from fastapi import ( APIRouter, Depends)

from app.db.session import SessionDep
from app.features.auth.dependencies import (
    get_current_auth_user,
    get_current_user,
)
from app.features.auth.schema import (
    SyncUserRequest,
)
from app.features.auth.services import (
    sync_user_service,
)
from app.features.users.models import User


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.get("/me")
async def me(
    user: Any = Depends(
        get_current_auth_user
    ),
):
    return user


@router.post("/sync-user",response_model=User,)
async def sync_user(
    payload: SyncUserRequest,
    session: SessionDep,
    auth_user: Any = Depends(
        get_current_auth_user
    ),
) -> User:
    return await sync_user_service(
        payload=payload,
        session=session,
        auth_user=auth_user,
    )

@router.get("/profile", response_model=User)
async def get_profile(
    session: SessionDep,
    user: User = Depends(get_current_user),
) -> User:
    """
    Returns the current authenticated user's DB profile.
    """
    return user