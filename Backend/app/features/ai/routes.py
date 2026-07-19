from fastapi import APIRouter, Depends, Query
from app.features.ai.service import create_ai_message, get_user_ai_messages
from app.features.ai.schemas import AIMessageRequest, AIMessageResponse, PaginatedAIMessages
from app.features.auth.dependencies import require_student
from app.features.users.models import User
from app.db.session import SessionDep
import uuid

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/chat", response_model=AIMessageResponse)
async def send_ai_message(
    body: AIMessageRequest,
    session: SessionDep,
    current_user: User = Depends(require_student),
) -> AIMessageResponse:
    response = await create_ai_message(session, current_user.id, body.message)
    return AIMessageResponse(response=response)


@router.get("/conversations", response_model=PaginatedAIMessages)
async def get_all_ai_messages(
    session: SessionDep,
    current_user: User = Depends(require_student),
    limit: int = Query(default=20, ge=1, le=100),
    cursor: uuid.UUID | None = Query(default=None),
):
    return await get_user_ai_messages(session, current_user.id, limit=limit, cursor=cursor)
