from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Index, Text
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel


class Review(SQLModel, table=True):
    __tablename__ = "reviews" #type: ignore

    __table_args__= (
        Index("idx_reviews_tutor", "tutor_id"),
        Index("idx_reviews_student", "student_id"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = Field(sa_column=Column(Text, nullable=True))
    tutor_id: uuid.UUID = Field(sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False))
    student_id: uuid.UUID = Field(sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False))
    session_id: Optional[uuid.UUID] =  Field(sa_column=Column(ForeignKey("sessions.id", ondelete="CASCADE"), nullable=True, unique=True))
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )
    )
    is_verified: bool = False