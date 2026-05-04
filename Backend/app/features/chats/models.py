import uuid
from datetime import datetime, timezone
from typing import Optional
from app.common.enums import chatMemberRole
from sqlmodel import SQLModel, Field, Index
from sqlalchemy import Column, Enum, DateTime, ForeignKey, Text, text
from sqlalchemy.sql import func

class Room(SQLModel, table=True):
    __tablename__ = "rooms" # type: ignore

    room_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    type: str = Field(sa_column=Column(Text, nullable=False)) # direct | group
    name: Optional[str] =  Field(sa_column=Column(Text, nullable=True))

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )
    )
    created_by: uuid.UUID = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    )



class RoomMember(SQLModel, table=True):
    __tablename__ = "room_members"  #type: ignore

    room_id: uuid.UUID =  Field(
    sa_column=Column(ForeignKey("rooms.room_id", ondelete="CASCADE"), nullable=False, primary_key=True)
)
    user_id: uuid.UUID =  Field(
    sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
)
    role: chatMemberRole = Field(
        sa_column=Column(Enum(chatMemberRole, name="chat_member_role"), nullable=False)
    )
    joined_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    __table_args__ = (
        Index("idx_room_members_user", "user_id"),
    )


class Message(SQLModel, table=True):  
    __tablename__ = "messages"  #type: ignore

    message_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    sender_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    )
    room_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("rooms.room_id", ondelete="CASCADE"), nullable=False)
    )
    content: str =  Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )
    )
    seen_at: datetime = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    is_deleted: bool = False

    __table_args__ = (
        Index("idx_messages_room_time", "room_id", text("created_at DESC")),
    )
