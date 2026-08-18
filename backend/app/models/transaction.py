import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Any
from sqlalchemy import String, Date, DateTime, Numeric, ForeignKey, text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.asset import Asset


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    
    # Foreign key referencing Asset
    asset_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Core columns: type (BUY/SELL/OTHER/etc.), trade_date, total_spent
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    total_spent: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    
    # Remaining data in JSONB (quantity, unit_price, total_costs, broker, notes, taxes, etc.)
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

    # Unidirectional relationship to Asset (Asset class does not receive FK to Transaction)
    asset: Mapped["Asset"] = relationship("Asset")
