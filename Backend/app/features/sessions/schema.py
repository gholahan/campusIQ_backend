from decimal import Decimal
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.common.enums import SessionStatus
from sqlmodel import Field


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
    meet_link: str | None
    started_at: datetime | None
    ended_at: datetime | None
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

class SessionParams(BaseModel):
    status: Optional[SessionStatus] = None

class AcceptSession(BaseModel):
    meet_link: str

class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=10)
    comment: str | None = None

class ReviewRead(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    rating: int
    comment: str | None
    created_at: datetime

