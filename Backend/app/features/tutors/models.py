from decimal import Decimal
import uuid
from typing import  Any, Dict, Optional
from sqlalchemy import Column, ForeignKey, Index, Numeric, Text
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB


class TutorProfile(SQLModel, table=True):
    __tablename__ = "tutor_profiles" #type: ignore

    __table_args__ = (
        Index("idx_tutor_profiles_rating", "average_rating"),
    )

    user_id: uuid.UUID = Field(
    sa_column=Column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        )
    )
    bio: Optional[str] = Field(
        sa_column=Column(Text, nullable=True)
    )
    hourly_rate: Decimal = Field(
        sa_column=Column(Numeric(10, 2), nullable=True)
    )
    availability: Optional[Dict[str, Any]] = Field(default=None,sa_column=Column(JSONB))
    is_online: bool = False
    average_rating: Decimal = Field(
        sa_column=Column(Numeric(3, 2), nullable=False)
    )

    review_count: int = 0
    total_sessions: int = 0
