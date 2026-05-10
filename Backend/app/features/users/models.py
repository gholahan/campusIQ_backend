import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Boolean, Column, Enum, Index, DateTime, Text
from sqlalchemy.sql import func
from app.common.enums import UserRole


class User(SQLModel, table=True):
    __tablename__ = "users" #type: ignore

    __table_args__ = (
        Index("idx_users_role", "role"),
    )

    id: uuid.UUID = Field(primary_key=True)

    role: UserRole = Field(
        sa_column=Column(Enum(UserRole, name="user_role"), nullable=False)
    )

    first_name: str = Field(sa_column=Column(Text, nullable=False))
    last_name: str = Field(sa_column=Column(Text, nullable=False))

    email: str = Field(
        sa_column=Column(Text, nullable=False, unique=True)
    )

    avatar_url: Optional[str] = Field(
        sa_column=Column(Text, nullable=True)
    )

    email_verified: bool = Field(
    default=False,
    sa_column=Column(
        Boolean,
        nullable=False,
        server_default="false",
    ),
)

    is_active: bool = Field(
        default=True,
        sa_column=Column(
            Boolean,
            nullable=False,
            server_default="true",
        ),
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    last_seen_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
)