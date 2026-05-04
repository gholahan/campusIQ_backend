from datetime import datetime
import uuid
from sqlalchemy import Column, Enum, ForeignKey, Index, DateTime, Text
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel
from app.common.enums import AiChatRole


class AIConversation(SQLModel, table=True):
    __tablename__ = "ai_conversations" #type: ignore

    __table_args__ = (
        Index("idx_ai_conversations_user", "user_id"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False))
    title: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(
    sa_column=Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        )
    )



class AIMessage(SQLModel, table=True):
    __tablename__ = "ai_messages" ##type: ignore

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(sa_column=Column(ForeignKey("ai_conversations.id", ondelete="CASCADE"),nullable=False))
    role: AiChatRole = Field(
        sa_column=Column(
            Enum(AiChatRole, name="ai_chat_role"),
            nullable=False,
        )
    )
    content:str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(
    sa_column=Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        )
    )


    __table_args__ = (
        Index("idx_ai_messages_convo", "conversation_id", "created_at"),
    )


class AICredit(SQLModel, table=True):
    __tablename__ = "ai_credits" #type: ignore

    user_id: uuid.UUID = Field(sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False, primary_key=True))
    used_today: int = 0
    daily_limit: int = 20
    last_reset: datetime = Field(
    sa_column=Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        )
    )

