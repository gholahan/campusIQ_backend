# app/features/auth/services.py

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlmodel import select

from app.db.session import SessionDep
from app.features.auth.schema import SyncUserRequest
from app.features.users.models import User


def parse_supabase_time(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

    raise TypeError(
        f"Invalid datetime value: {type(value)}"
    )


async def sync_user_service(
    payload: SyncUserRequest,
    session: SessionDep,
    auth_user: Any,
) -> User:
    user_id = uuid.UUID(str(auth_user.id))

    statement = select(User).where(
        User.id == user_id
    )

    result = await session.exec(statement)

    existing_user = result.first()

    if existing_user:
        return existing_user

    # ---------------------------------
    # Metadata normalization
    # ---------------------------------

    metadata_raw:dict[str, Any] = auth_user.user_metadata or {}
    app_metadata_raw:dict[str, Any] = auth_user.app_metadata or {}

    metadata: dict[str, Any] = dict(metadata_raw)
    app_metadata: dict[str, Any] = dict(
        app_metadata_raw
    )

    provider = app_metadata.get("provider")

    avatar_url_raw = (
        metadata.get("avatar_url")
        or metadata.get("picture")
    )

    avatar_url = (
        str(avatar_url_raw)
        if avatar_url_raw is not None
        else None
    )

    # ---------------------------------
    # Names
    # ---------------------------------

    first_name = payload.first_name
    last_name = payload.last_name

    if provider == "google":
        full_name_raw = (
            metadata.get("full_name")
            or metadata.get("name")
        )

        full_name = (
            str(full_name_raw)
            if full_name_raw is not None
            else None
        )

        if full_name:
            parts = full_name.split(" ", 1)

            first_name = parts[0]

            if len(parts) > 1:
                last_name = parts[1]

    # ---------------------------------
    # Datetime normalization
    # ---------------------------------

    created_at = parse_supabase_time(
        auth_user.created_at
    )

    updated_at = parse_supabase_time(
        auth_user.updated_at
    )

    last_seen_raw = (
        auth_user.last_sign_in_at
        or auth_user.created_at
    )

    last_seen_at = parse_supabase_time(
        last_seen_raw
    )

    # ---------------------------------
    # Create user
    # ---------------------------------

    user = User(
        id=user_id,

        role=payload.role,

        first_name=first_name,
        last_name=last_name,

        email=str(auth_user.email),

        avatar_url=avatar_url,

        email_verified=(
            auth_user.email_confirmed_at
            is not None
        ),

        created_at=created_at,
        updated_at=updated_at,
        last_seen_at=last_seen_at,
    )

    session.add(user)

    await session.commit()

    await session.refresh(user)

    return user


async def update_last_seen(session: SessionDep, user: User):
    user.last_seen_at = datetime.now(timezone.utc)
    session.add(user)
    await session.commit()
    return user

async def get_user_by_id(session: SessionDep, user_id: uuid.UUID):
    return await session.get(User, user_id)

def ensure_owner(resource_user_id: uuid.UUID, current_user_id: uuid.UUID):
    if resource_user_id != current_user_id:
        raise HTTPException(403)