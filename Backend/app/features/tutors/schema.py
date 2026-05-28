from decimal import Decimal
from typing import Any
import uuid
from datetime import time
from enum import Enum
from typing import Dict, List
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.features.courses.schema import CourseRead



class FullDayKey(str, Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"


class DayWindow(BaseModel):
    start: time
    end: time


class TutorProfileCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)

    title: str = Field(..., min_length=2, max_length=120)

    bio: str = Field(..., min_length=10)

    hourly_rate: float = Field(..., gt=0)

    availability: Dict[FullDayKey, DayWindow]

    courses: List[str] = Field(default_factory=list)

    @field_validator("courses", mode="before")
    @classmethod
    def lowercase_courses(cls, v: List[str]) -> List[str]:
        return [c.lower() for c in v]


class TutorProfileUpdate(BaseModel):
    bio: str | None = Field(default=None, min_length=10)

    hourly_rate: Decimal | None = Field(default=None, gt=0)

    availability: Dict[FullDayKey, DayWindow] | None = None

    courses: list[str] | None = None

    @field_validator("courses", mode="before")
    @classmethod
    def lowercase_courses(cls, v: list[str] | None) -> list[str] | None:
        return [c.lower() for c in v] if v is not None else None

    is_online: bool | None = None


class TutorSearchParams(BaseModel):
    q: str | None = None  # 👈 NEW GLOBAL SEARCH

    name: str | None = None
    course: str | None = None

    is_online: bool | None = None
    min_rate: float | None = Field(default=None, gt=0)
    max_rate: float | None = Field(default=None, gt=0)
    min_rating: float | None = Field(default=None, ge=0, le=5)

    order_by: str | None = Field(default=None, pattern="^(average_rating|hourly_rate)$")
    order_dir: str = Field(default="desc", pattern="^(asc|desc)$")

    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class TutorSearchResult(BaseModel):
    total: int
    tutors: list["TutorProfileRead"]


class TutorProfileRead(BaseModel):
    user_id: uuid.UUID
    full_name: str              # from User.first_name + last_name
    title: str  | None           # from TutorProfile or User
    bio: str 
    hourly_rate: Decimal | None
    availability: dict[str, Any] | None
    is_online: bool
    average_rating: Decimal
    review_count: int
    total_sessions: int
    courses: list[CourseRead]

    model_config = ConfigDict(from_attributes=True)