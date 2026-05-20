# app/features/auth/dependencies.py

import uuid
from typing import Any

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from supabase import create_client
from sqlmodel import select
from app.common.enums import UserRole
from app.core.config import (
    SUPABASE_KEY,
    SUPABASE_URL,
)
from app.db.session import SessionDep
from app.features.users.models import User


# ---------------------------------------------------
# Supabase client
# ---------------------------------------------------

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY must be set"
    )

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)

security = HTTPBearer()


# ---------------------------------------------------
# Get authenticated Supabase user
# ---------------------------------------------------

async def get_current_auth_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    response = supabase.auth.get_user(token)

    if not response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    auth_user = response.user

    if not auth_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return auth_user


# ---------------------------------------------------
# Get current DB user
# ---------------------------------------------------

async def get_current_user(
    session: SessionDep,
    auth_user: Any = Depends(
        get_current_auth_user
    ),
) -> User:
    user_id = uuid.UUID(auth_user.id)

    statement = select(User).where(
        User.id == user_id
    )

    result = await session.exec(statement)

    user = result.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


# ---------------------------------------------------
# Role Guards : depend on get_current_user that in return deends on get_current_auth_use
# ---------------------------------------------------

async def require_admin(
    user: User = Depends(get_current_user),
) -> User:
    if user.role != UserRole.admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    return user


async def require_student(
    user: User = Depends(get_current_user),
) -> User:
    if user.role != UserRole.student:
        raise HTTPException(
            status_code=403,
            detail="Student access required",
        )

    return user


async def require_tutor(
    user: User = Depends(get_current_user),
) -> User:
    if user.role != UserRole.tutor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tutor access required",
        )

    return user