from decimal import Decimal
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.common.enums import SessionStatus


class ScheduledAt(BaseModel):
    day: str
    start: str
    end: str

class SessionCreate(BaseModel):
    tutor_id: uuid.UUID
    subject: str
    duration: float
    cost: Decimal
    scheduled_at: ScheduledAt
    notes: Optional[str] = None

class SessionTutorRead(BaseModel):
    id: uuid.UUID
    full_name: str
    profile_picture_url: str | None


class SessionRead(BaseModel):
    id: uuid.UUID
    subject: str
    duration: float
    notes: str | None
    status: SessionStatus
    cost: float
    tutor: SessionTutorRead
    scheduled_at: ScheduledAt
    created_at: datetime

class PostSessionResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    tutor_id: uuid.UUID
    subject: str
    duration: float
    scheduled_at: ScheduledAt
    notes: Optional[str]
    status: SessionStatus
    cost: Optional[Decimal]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
