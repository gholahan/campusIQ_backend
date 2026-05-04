from datetime import datetime
from typing import Any, Dict, Optional
import uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, DateTime, Index, Text
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID

class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs" #type:ignore

    __table_args__ = (
     Index("idx_audit_created_at", "created_at"),
     Index("idx_audit_admin", "actor_id"),
    )
    

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    actor_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("users.id"), nullable=False)
    )

    action: str = Field(
        sa_column=Column(Text, nullable=False)
    )

    target_type: str = Field(
        sa_column=Column(Text, nullable=False)
    )

    target_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(UUID(as_uuid=True), nullable=True)
    )

    details: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True)
    )

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )
    )
