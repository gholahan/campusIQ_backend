# from datetime import datetime, timezone
# from typing import List, Optional
# import uuid

# from sqlalchemy import Column, DateTime, Text, func
# from sqlmodel import Field, Relationship, SQLModel

# from app.features.tutors.models import TutorCourse


# class Course(SQLModel, table=True):
#     __tablename__ = "courses"  # type: ignore

#     id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

#     name: str = Field(
#         sa_column=Column(Text, nullable=False, unique=True)
#     )

#     created_at: datetime = Field(
#         default_factory=lambda: datetime.now(timezone.utc),
#         sa_column=Column(
#             DateTime(timezone=True),
#             nullable=False,
#             server_default=func.now(),
#         ),
#     )

#     tutors: list["TutorProfile"] = Relationship(
#         back_populates="courses",
#         link_model=TutorCourse,
#     )