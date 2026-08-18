from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.domain.constants.asset import STANDARD_ASSET_TYPES


class AssetBase(BaseModel):
    """Base fields shared across Asset input schemas (Create/Update)."""
    id: str = Field(..., description="Unique asset identifier / ticker (e.g. PETR4, HGLG11, BTC, CDB_INTER_2029)", min_length=1, max_length=50)
    name: str = Field(..., description="Asset name as STRING (e.g. Petróleo Brasileiro S.A. - Petrobras, CSHG Logística FII)", min_length=1, max_length=150)
    type: str = Field(..., description="Asset type as STRING (e.g. ACOES, FII, FIAGRO, FIINFRA, RENDA_FIXA, TESOURO, ETF, FUNDO, CRIPTO, OTHER)", min_length=1, max_length=50)
    metadata_json: Dict[str, Any] = Field(
        default_factory=dict,
        description="Remaining data stored in JSONB (currency, sector, segment, strategy tags, CNPJ, target allocation %, etc.)"
    )

    @field_validator("id")
    @classmethod
    def normalize_id(cls, v: str) -> str:
        cleaned = v.strip().upper()
        if not cleaned:
            raise ValueError("Asset ID / ticker cannot be empty.")
        return cleaned

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
    """Response schema — reads from DB without re-validating domain rules on output."""
    id: str
    name: str
    type: str
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
