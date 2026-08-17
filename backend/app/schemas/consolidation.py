import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class AssetPosition(BaseModel):
    asset_id: str
    name: Optional[str] = None
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


# --- Typed JSONB Consolidation Data Items ---

class StockConsolidationItem(BaseModel):
    ticker: str = Field(..., description="Stock ticker (e.g. BBAS3, PETR4)")
    name: Optional[str] = Field(default=None, description="Company name (e.g. Banco do Brasil S.A.)")
    quantity: Decimal = Field(..., description="Quantity of shares held", gt=0)
    average_price: Decimal = Field(..., description="Average purchase price (Preço Médio)", ge=0)
    type: str = Field(default="ON", description="Share type: ON, PN, UNIT, BDR")
    custody: str = Field(default="DEFAULT", description="Broker or custodian (e.g. XP, BTG, Inter)")
    currency: str = Field(default="BRL", description="Currency (BRL, USD)")
    total_invested: Optional[Decimal] = None


class FundConsolidationItem(BaseModel):
    ticker: str = Field(..., description="Fund ticker (e.g. HGLG11, KNIP11)")
    name: Optional[str] = Field(default=None, description="Fund name (e.g. CSHG Logística FII)")
    quantity: Decimal = Field(..., description="Quantity of quotas held", gt=0)
    average_price: Decimal = Field(..., description="Average quota price", ge=0)
    type: str = Field(default="FII", description="Fund type: FII, FIAGRO, FI_INFRA, ETF, MUTUAL_FUND")
    custody: str = Field(default="DEFAULT", description="Broker or custodian")
    currency: str = Field(default="BRL", description="Currency")
    total_invested: Optional[Decimal] = None


class FixedIncomeConsolidationItem(BaseModel):
    name: str = Field(..., description="Asset title (e.g. Tesouro Selic 2029, CDB Inter 110% CDI)")
    issuer: Optional[str] = Field(default=None, description="Issuer institution (e.g. Tesouro Nacional, Banco Inter)")
    type: str = Field(..., description="Asset type: TREASURY, CDB, LCI, LCA, CRI, CRA, DEBENTURE")
    indexer: str = Field(..., description="Benchmark indexer: SELIC, CDI, IPCA, PRE")
    rate: Optional[str] = Field(default=None, description="Agreed rate (e.g. '115% CDI', 'IPCA + 6.5%', '13.0% a.a.')")
    purchase_date: Optional[str] = Field(default=None, description="Date of purchase (YYYY-MM-DD)")
    maturity_date: Optional[str] = Field(default=None, description="Maturity date (YYYY-MM-DD)")
    quantity: Decimal = Field(default=Decimal("1.0"), description="Quantity/Titles held", gt=0)
    invested_amount: Decimal = Field(..., description="Total principal amount invested", ge=0)
    current_value: Optional[Decimal] = Field(default=None, description="Current marked-to-market value")
    custody: str = Field(default="DEFAULT", description="Broker or custodian")
    currency: str = Field(default="BRL", description="Currency")


class CryptoConsolidationItem(BaseModel):
    ticker: str = Field(..., description="Crypto symbol (e.g. BTC, ETH, SOL)")
    name: Optional[str] = Field(default=None, description="Crypto name (e.g. Bitcoin)")
    quantity: Decimal = Field(..., description="Coins/Tokens held", gt=0)
    average_price: Decimal = Field(..., description="Average purchase price in currency", ge=0)
    custody: str = Field(default="DEFAULT", description="Wallet or Exchange (e.g. Cold Wallet, Binance)")
    currency: str = Field(default="BRL", description="Reference currency")
    total_invested: Optional[Decimal] = None


class InternationalConsolidationItem(BaseModel):
    ticker: str = Field(..., description="US/Global ticker (e.g. VOO, AAPL)")
    name: Optional[str] = Field(default=None, description="Asset name")
    quantity: Decimal = Field(..., description="Shares held", gt=0)
    average_price: Decimal = Field(..., description="Average price in USD", ge=0)
    type: str = Field(default="STOCK", description="STOCK, ETF, REIT, ADR")
    custody: str = Field(default="Avenue", description="Offshore broker (e.g. Avenue, IBKR, Schwab)")
    currency: str = Field(default="USD", description="Currency (default USD)")
    total_invested: Optional[Decimal] = None


class CashConsolidationItem(BaseModel):
    account: str = Field(..., description="Account description (e.g. Reserva de Emergência, Conta Corrente)")
    institution: str = Field(..., description="Bank/Institution (e.g. Nubank, Itaú, BTG)")
    amount: Decimal = Field(..., description="Balance amount", ge=0)
    currency: str = Field(default="BRL", description="Currency")


class ConsolidationDataPayload(BaseModel):
    summary: Optional[Dict[str, Any]] = Field(default_factory=dict)
    stocks: List[StockConsolidationItem] = Field(default_factory=list)
    funds: List[FundConsolidationItem] = Field(default_factory=list)
    fixed_income: List[FixedIncomeConsolidationItem] = Field(default_factory=list)
    crypto: List[CryptoConsolidationItem] = Field(default_factory=list)
    international: List[InternationalConsolidationItem] = Field(default_factory=list)
    cash: List[CashConsolidationItem] = Field(default_factory=list)


# --- Database Entity Schemas ---

class ConsolidationBase(BaseModel):
    type: str = Field(..., description="Consolidation type (e.g. ANNUAL, MONTHLY, TAX, PORTFOLIO)", min_length=1, max_length=50)
    year: int = Field(..., description="Reference year (e.g. 2024)")
    version: int = Field(default=1, description="Version number of this consolidation snapshot", ge=1)
    data: Dict[str, Any] = Field(default_factory=dict, description="Consolidated snapshot payload (JSONB)")


class ConsolidationCreate(ConsolidationBase):
    pass


class ConsolidationUpdate(BaseModel):
    type: Optional[str] = None
    year: Optional[int] = None
    version: Optional[int] = None
    data: Optional[Dict[str, Any]] = None


class ConsolidationResponse(ConsolidationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

