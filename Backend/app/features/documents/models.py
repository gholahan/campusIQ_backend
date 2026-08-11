import uuid
from datetime import datetime, timezone
# from typing import Any
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, Text, Enum, UniqueConstraint
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel
from pgvector.sqlalchemy import Vector
from app.common.enums import DocumentStatus




class Document(SQLModel, table=True):
    __tablename__ = "documents" #type: ignore

    __table_args__ = (
        Index("idx_documents_user_id", "user_id"),
        Index("idx_documents_conversation_id", "conversation_id"),
        Index("idx_documents_course_id", "course_id"),
        Index("idx_documents_status", "status"),
    )

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )

    # Who uploaded it
    user_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        )
    )

    conversation_id: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(
            ForeignKey(
                "ai_conversations.id",
                ondelete="CASCADE"
            ),
            nullable=True,
        )
    )

    course_id: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(
            ForeignKey("courses.id", ondelete="CASCADE"),
            nullable=True,
        )
    )

    file_name: str = Field(
        sa_column=Column(Text, nullable=False)
    )

    file_url: str = Field(
        sa_column=Column(Text, nullable=False)
    )

    status: DocumentStatus = Field(
        default=DocumentStatus.processing,
        sa_column=Column(
            Enum(
                DocumentStatus,
                name="document_status",
                native_enum=True,
            ),
            nullable=False,
        )
    )
    page_count: int | None = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        )
    )


class DocumentChunk(SQLModel, table=True):
    __tablename__ = "document_chunks"  # type: ignore

    __table_args__ = (
    Index("idx_chunks_document_id", "document_id"),
    Index("idx_chunks_page_number", "page_number"),
    UniqueConstraint(
        "document_id",
        "chunk_index",
        name="uq_document_chunk_index",
    ),
)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    document_id: uuid.UUID = Field(
        sa_column=Column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    )

    text: str = Field(sa_column=Column(Text, nullable=False))

    embedding: list[float] = Field(
        sa_column=Column(Vector(1024), nullable=False)
    )


    page_number: int | None = Field(
        default=None,
        sa_column=Column(Integer, nullable=True)
    )

    chunk_index: int = Field(
        sa_column=Column(Integer, nullable=False)
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )