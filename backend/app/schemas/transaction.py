from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator

VALID_TRANSACTION_TYPES = {
    "BUY",
    "SELL",
    "OTHER",
    "DIVIDEND",
    "JCP",
    "SPLIT",
    "BONUS",
    "AMORTIZATION",
}


class TransactionBase(BaseModel):
    # Foreign Key to Asset (Integer ID)
    asset_id: int = Field(..., description="Target asset ID (FK to Asset integer ID)", ge=1)
    
    # Core columns
    type: str = Field(..., description="Operation type (BUY, SELL, OTHER, DIVIDEND, JCP, SPLIT, BONUS, AMORTIZATION)", min_length=1, max_length=20)
    trade_date: date = Field(..., description="Date of the transaction (YYYY-MM-DD)")
    total_spent: Decimal = Field(default=Decimal("0.0000"), description="Total spent / invested / transacted amount", ge=0)
    
    # Remaining data in JSONB (quantity, unit_price, total_costs, broker, taxes withheld, notes)
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Remaining data stored in JSONB (quantity, unit_price, total_costs, broker, etc.)"
    )

    @field_validator("type")
    @classmethod
    def validate_transaction_type(cls, v: str) -> str:
        cleaned = v.strip().upper()
        if cleaned not in VALID_TRANSACTION_TYPES:
            raise ValueError(
                f"Invalid transaction type '{cleaned}'. Allowed types: {', '.join(sorted(VALID_TRANSACTION_TYPES))}"
            )
        return cleaned

    @model_validator(mode="after")
    def validate_financial_math_and_contracts(self) -> "TransactionBase":
        tx_type = self.type.upper()
        details = self.details or {}
        
        qty = Decimal(str(details.get("quantity", "0"))) if "quantity" in details else Decimal("0")
        unit_price = Decimal(str(details.get("unit_price", "0"))) if "unit_price" in details else Decimal("0")
        total_costs = Decimal(str(details.get("total_costs", "0"))) if "total_costs" in details else Decimal("0")

        if tx_type in ["BUY", "SELL"]:
            if qty <= 0 and "quantity" in details:
                raise ValueError(f"Transaction type '{tx_type}' requires quantity > 0.")
            if unit_price < 0:
                raise ValueError("Unit price cannot be negative.")
            if total_costs < 0:
                raise ValueError("Total costs/fees cannot be negative.")

            # Auto-calculate total_spent if not explicitly provided but qty and unit_price are available
            expected_spent = (qty * unit_price) + total_costs
            if self.total_spent == Decimal("0") and expected_spent > Decimal("0"):
                self.total_spent = expected_spent
            elif expected_spent > Decimal("0") and self.total_spent > Decimal("0"):
                # Check discrepancy between total_spent and computed math (tolerance of R$ 0.10)
                diff = abs(self.total_spent - expected_spent)
                if diff > Decimal("0.10"):
                    raise ValueError(
                        f"Financial math discrepancy: total_spent ({self.total_spent}) does not match "
                        f"(quantity {qty} * unit_price {unit_price}) + costs {total_costs} = {expected_spent} (diff: {diff})"
                    )

        elif tx_type in ["SPLIT", "BONUS"]:
            if self.total_spent > Decimal("0"):
                raise ValueError(f"Corporate event '{tx_type}' must have total_spent = 0.00.")
            if qty <= 0 and "quantity" in details:
                raise ValueError(f"Corporate event '{tx_type}' requires additional share quantity > 0.")

        elif tx_type in ["DIVIDEND", "JCP"]:
            if self.total_spent <= Decimal("0") and (qty <= Decimal("0") or unit_price <= Decimal("0")):
                raise ValueError(f"Income event '{tx_type}' must specify positive total_spent or quantity * unit_price.")

        return self


class TransactionCreate(TransactionBase):
    pass


class TransactionBulkCreate(BaseModel):
    transactions: List[TransactionCreate] = Field(..., min_length=1)


class TransactionResponse(TransactionBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
