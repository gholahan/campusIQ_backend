from decimal import Decimal
import uuid
from typing import Any, Dict, List, Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, ForeignKey, Index, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from datetime import datetime, timezone


class TutorCourse(SQLModel, table=True):
    __tablename__ = "tutor_courses"  # type: ignore

    tutor_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("tutor_profiles.user_id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )
    course_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("courses.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )


class TutorProfile(SQLModel, table=True):
    __tablename__ = "tutor_profiles"  # type: ignore
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
    full_name: str = Field(sa_column=Column(Text, nullable=False))
    title: str| None = Field(sa_column=Column(Text, nullable=True))
    bio: str = Field(sa_column=Column(Text, nullable=False))
    hourly_rate: Optional[Decimal] = Field(
        sa_column=Column(Numeric(10, 2), nullable=True)
    )
    availability: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB)
    )
    is_online: bool = False
    average_rating: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(Numeric(3, 2), nullable=False),
    )
    review_count: int = 0
    total_sessions: int = 0

    courses: Optional[List["Course"]] = Relationship(
        back_populates="tutors",
        link_model=TutorCourse,
    )


class Course(SQLModel, table=True):
    __tablename__ = "courses"  # type: ignore

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(sa_column=Column(Text, nullable=False, unique=True))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )

    tutors: Optional[List["TutorProfile"]] = Relationship(
        back_populates="courses",
        link_model=TutorCourse,
    )