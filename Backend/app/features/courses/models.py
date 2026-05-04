import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field, Index
from sqlalchemy import Column, DateTime, ForeignKey, Text
from sqlalchemy.sql import func


class Course(SQLModel, table=True):
    __tablename__ = "courses" #type: ignore

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(sa_column=Column(Text, nullable=False, unique=True))
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )
    )


class TutorCourse(SQLModel, table=True):
    __tablename__ = "tutor_courses" #type: ignore

    tutor_id: uuid.UUID =  Field(
        sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"),primary_key=True, nullable=False)
    )
    course_id: uuid.UUID =  Field(
        sa_column=Column(ForeignKey("courses.id", ondelete="CASCADE"),primary_key=True, nullable=False)
    )

    __table_args__ = (
        Index("idx_tutor_courses_course", "course_id"),
    )
