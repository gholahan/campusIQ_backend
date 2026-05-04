from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy import Column, Enum, DateTime, Index, Text
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel

from app.common.enums import ReportStatus


class ModerationReport(SQLModel, table=True):
    __tablename__ = "moderation_reports" # type:ignore

    __table_args__ = (
        Index("idx_reports_status","status"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    reporter_id: uuid.UUID = Field(default=None, foreign_key="users.id")
    target_type: str = Field(sa_column=Column(Text, nullable=False))
    target_id: Optional[uuid.UUID] = None
    reason: str = Field(sa_column=Column(Text, nullable=False))
    severity: int 
    status: ReportStatus = Field(
        sa_column=Column(
            Enum(ReportStatus, name="report_status"),
            default=ReportStatus.pending,
            nullable=False,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )
    )
