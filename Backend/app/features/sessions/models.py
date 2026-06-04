import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import Column, Enum, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlmodel import SQLModel, Field
from app.common.enums import SessionStatus

class Session(SQLModel, table=True):
    __tablename__ = "sessions" #type: ignore

    __table_args__ = (
        Index("idx_sessions_student", "student_id"),
        Index("idx_sessions_tutor", "tutor_id"),
        Index("idx_sessions_status", "status"),
        Index("idx_sessions_created_at", "created_at"),
    )
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    student_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    )

    tutor_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    )

    subject: str = Field(sa_column=Column(Text, nullable=False))

    duration: float = Field(nullable=False)  # matches your frontend

    scheduled_at: Dict[str, Any] = Field(
        sa_column=Column(JSONB, nullable=False)
    )

    notes: Optional[str] = Field(sa_column=Column(Text, nullable=True))

    status: SessionStatus = Field(
        default=SessionStatus.pending,
        sa_column=Column(Enum(SessionStatus, name="session_status"), nullable=False),
    )

    cost: float = Field(nullable=False)

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    ) 