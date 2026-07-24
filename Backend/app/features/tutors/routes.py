import uuid
from fastapi import APIRouter, Depends, Query

from app.features.users.models import User
from app.db.session import SessionDep
from app.features.auth.dependencies import get_current_user, require_tutor
from app.features.tutors.schema import (
    TutorProfileCreate,
    TutorProfileRead,
    TutorProfileUpdate,
    TutorSearchParams,
    TutorSearchResult,
)
from app.features.tutors.service import (
    create_tutor_profile_service,
    get_tutor_profile_response,
    search_tutors_service,
    update_tutor_profile_service,
)

router = APIRouter(prefix="/tutors", tags=["Tutors"])


@router.post("/profile", response_model=TutorProfileRead)
async def create_tutor_profile(
    payload: TutorProfileCreate,
    session: SessionDep,
    auth_user: User = Depends(require_tutor),
):
    return await create_tutor_profile_service(
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


@router.get("/search", response_model=TutorSearchResult)
async def search_tutors(
    session: SessionDep,
    q: str | None = Query(default=None),
    name: str | None = Query(default=None),
    course: str | None = Query(default=None),
    is_online: bool | None = Query(default=None),
    min_rate: float | None = Query(default=None, gt=0),
    max_rate: float | None = Query(default=None, gt=0),
    min_rating: float | None = Query(default=None, ge=0, le=5),
    order_by: str | None = Query(default=None, pattern="^(average_rating|hourly_rate)$"),
    order_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    auth_user: User = Depends(get_current_user), # auth gate only  
):
    params = TutorSearchParams(
        q=q,
        name= name,
        course=course,
        is_online=is_online,
        min_rate=min_rate,
        max_rate=max_rate,
        min_rating=min_rating,
        order_by=order_by,
        order_dir=order_dir,
        offset=offset,
        limit=limit,
    )
    return await search_tutors_service(session=session, params=params)

@router.get("/{tutor_id}", response_model=TutorProfileRead)
async def get_tutor_by_id(
    tutor_id: uuid.UUID,
    session: SessionDep,
    auth_user: User = Depends(get_current_user),
):
    return await get_tutor_profile_response(session, tutor_id)
