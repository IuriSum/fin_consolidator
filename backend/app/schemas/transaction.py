from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, Any, Optional, List
import uuid
from pydantic import BaseModel, Field, ConfigDict


class OperationType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    JCP = "JCP"
    SPLIT = "SPLIT"
    BONUS = "BONUS"
    AMORTIZATION = "AMORTIZATION"
    SUBSCRIPTION = "SUBSCRIPTION"


class TransactionBase(BaseModel):
    asset_id: str = Field(..., description="Target asset ticker / identifier", min_length=1, max_length=50)
    
    # Obligatory fields
    trade_date: date = Field(..., description="Date of the operation (YYYY-MM-DD)")
    operation_type: OperationType = Field(..., description="Type of operation")
    
    # Financial precision
    quantity: Decimal = Field(..., description="Asset quantity with high precision", gt=0)
    unit_price: Decimal = Field(..., description="Unit price per share / asset", ge=0)
    total_costs: Decimal = Field(default=Decimal("0.0000"), description="Fees, brokerage, emoluments, taxes", ge=0)
    
    broker: Optional[str] = Field(default=None, max_length=50, description="Broker or custodian name")
    
    # JSONB default to {}
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dynamic transaction details (taxes withheld, broker note number, IRRF, etc.)"
    )


class TransactionCreate(TransactionBase):
    pass


class TransactionBulkCreate(BaseModel):
    transactions: List[TransactionCreate] = Field(..., min_length=1)


class TransactionResponse(TransactionBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
