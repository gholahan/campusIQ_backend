from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from app.common.enums import AiChatRole


class  AIMessageRequest (BaseModel):
    message: str = Field(..., min_length=1, max_length=200)


class AIMessageResponse(BaseModel):
    response: str


class ConversationRead(BaseModel):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class AIMessageRead(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: AiChatRole
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AICreditRead(BaseModel):
    user_id: uuid.UUID
    used_today: int
    daily_limit: int
    last_reset: datetime

    model_config = {"from_attributes": True}


class PaginatedAIMessages(BaseModel):
    messages: list[AIMessageRead]
    next_cursor: uuid.UUID | None
