from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class AssetBase(BaseModel):
    id: str = Field(..., description="Unique asset identifier / ticker (e.g. PETR4, HGLG11, BTC, CDB_INTER_2029)", min_length=1, max_length=50)
    asset_type: str = Field(..., description="Asset class (e.g. STOCK, FII, FIXED_INCOME, TREASURY, CRYPTO, OFFSHORE)", min_length=1, max_length=30)
    currency: str = Field(default="BRL", min_length=3, max_length=3)
    metadata_json: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary multi-classification data, sector, strategy tags, target allocation %, etc."
    )


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    asset_type: Optional[str] = None
    currency: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None


class AssetResponse(AssetBase):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
