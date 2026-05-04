from decimal import Decimal
import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Enum, DateTime, ForeignKey, Index, Numeric, Text
from sqlalchemy.sql import func
from app.common.enums import PaymentStatus


class Payment(SQLModel, table=True):
    __tablename__ = "payments" # type: ignore

    __table_args__ = (
        Index("idx_payments_user", "payer_id"),
        Index("idx_payments_status", "status"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    session_id: uuid.UUID = Field(
        sa_column=Column(
            ForeignKey("sessions.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        )
    )
    payer_id: uuid.UUID =  Field(
        sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    )
    amount: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    currency: str = Field(sa_column=Column(Text, nullable=False, server_default="USD"))
    provider: Optional[str] = Field(sa_column=Column(Text, nullable=True))
    provider_ref: str =  Field(sa_column=Column(Text, nullable=False))
    status: PaymentStatus = Field(
        sa_column=Column(
            Enum(PaymentStatus, name="payment_status"),
            default=PaymentStatus.pending,
            nullable=False,
        )
    )
    paid_at: Optional[datetime] = None
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )
    )
