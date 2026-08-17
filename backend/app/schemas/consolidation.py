from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class AssetPosition(BaseModel):
    asset_id: str
    asset_type: str
    currency: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Computed metrics
    current_quantity: Decimal
    average_price: Decimal
    total_invested: Decimal
    total_costs_paid: Decimal
    total_dividends_received: Decimal
    total_jcp_received: Decimal
    
    # Transactions count
    total_transactions: int
    last_trade_date: Optional[str] = None


class PortfolioConsolidationResponse(BaseModel):
    consolidated_at: datetime
    total_portfolio_invested: Decimal
    total_portfolio_dividends: Decimal
    total_portfolio_jcp: Decimal
    total_assets_count: int
    
    # Breakdown by asset type
    by_asset_type: Dict[str, Dict[str, Any]]
    
    # Detailed list of positions
    positions: List[AssetPosition]
