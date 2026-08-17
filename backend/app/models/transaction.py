import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Any
from sqlalchemy import String, Date, DateTime, Numeric, ForeignKey, text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    
    asset_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Obligatory Fields
    trade_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    operation_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Financial precision fields (Decimal)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    total_costs: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        default=Decimal("0.0000"),
        server_default="0.0000"
    )
    
    broker: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # JSONB default to {}
    details: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb")
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    asset: Mapped["Asset"] = relationship("Asset", back_populates="transactions")
