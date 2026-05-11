# app/features/tutors/routes.py

from typing import Any

from fastapi import APIRouter, Depends

from app.db.session import SessionDep
from app.features.auth.dependencies import (
    get_current_auth_user,
)
from app.features.tutors.service import (
    sync_tutor_profile_service,
)

router = APIRouter(
    prefix="/tutors",
    tags=["tutors"],
)


@router.post("/sync")
async def sync_tutor(
    payload: dict[str, Any],
    session: SessionDep,
    auth_user: Any = Depends(get_current_auth_user),
):
    return await sync_tutor_profile_service(
        session=session,
        auth_user=auth_user,
        payload=payload,
    )