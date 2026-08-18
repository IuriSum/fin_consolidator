from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from app.domain.constants.asset import STANDARD_ASSET_TYPES

TICKER_TYPES = {"ACOES", "FII", "FIAGRO", "FIINFRA", "ETF"}


class AssetBase(BaseModel):
    """
    Base fields shared across Asset input schemas (Create/Update).
    Domain Rule (documented in domain/documentation.md):
    - All assets have a name.
    - If the asset is a stock or fund (ACOES, FII, FIAGRO, FIINFRA, ETF), 'name' contains the ticker.
    - 'metadata_json' contains 'company', 'cnpj', 'quantity', 'medium_price'.
    """
    name: str = Field(..., description="Asset ticker (for stocks/funds) or descriptive name (for fixed income/crypto)", min_length=1, max_length=150)
    type: str = Field(..., description="Asset type as STRING (ACOES, FII, FIAGRO, FIINFRA, RENDA_FIXA, TESOURO, ETF, FUNDO, CRIPTO, OTHER)", min_length=1, max_length=50)
    metadata_json: Dict[str, Any] = Field(
        default_factory=dict,
        description="Remaining data stored in JSONB (company, cnpj, quantity, medium_price, etc.)"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Asset name cannot be empty.")
        return cleaned

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        cleaned = v.strip().upper()
        if cleaned not in STANDARD_ASSET_TYPES:
            raise ValueError(
                f"Invalid asset type '{cleaned}'. Allowed standard types are: {', '.join(STANDARD_ASSET_TYPES)}"
            )
        return cleaned

    @model_validator(mode="after")
    def apply_ticker_casing(self) -> "AssetBase":
        if self.type in TICKER_TYPES:
            self.name = self.name.upper()
        return self


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            if not cleaned:
                raise ValueError("Asset name cannot be empty.")
            return cleaned
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip().upper()
            if cleaned not in STANDARD_ASSET_TYPES:
                raise ValueError(
                    f"Invalid asset type '{cleaned}'. Allowed standard types are: {', '.join(STANDARD_ASSET_TYPES)}"
                )
            return cleaned
        return v


class AssetResponse(BaseModel):
    """Response schema with Integer ID."""
    id: int
    name: str
    type: str
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
