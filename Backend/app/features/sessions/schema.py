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


class SessionResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    tutor_id: uuid.UUID
    subject: str
    duration: int
    scheduled_at: ScheduledAt
    notes: Optional[str]
    status: SessionStatus
    cost: Optional[Decimal]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
