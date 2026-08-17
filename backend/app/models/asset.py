from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy import String, DateTime, text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    asset_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="BRL", server_default="BRL")
    
    # Flexible multi-classification and tags default to {}
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(
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

    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="asset",
        cascade="all, delete-orphan",
        order_by="Transaction.trade_date.asc()"
    )
