from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.asset import Asset
from app.models.transaction import Transaction
from app.schemas.consolidation import PortfolioConsolidationResponse
from app.services.polars_engine import calculate_portfolio_consolidation

router = APIRouter(prefix="/portfolio", tags=["Portfolio Consolidation"])


@router.get("/consolidation", response_model=PortfolioConsolidationResponse)
async def get_portfolio_consolidation(db: AsyncSession = Depends(get_db)):
    """
    Executes the high-performance Polars calculation engine
    over the entire transactional ledger and returns the
    consolidated multi-classified JSON portfolio state.
    """
    # Fetch all assets
    assets_result = await db.execute(select(Asset))
    assets = assets_result.scalars().all()

    # Fetch all transactions ordered chronologically
    tx_result = await db.execute(
        select(Transaction).order_by(Transaction.trade_date.asc(), Transaction.created_at.asc())
    )
    transactions = tx_result.scalars().all()

    # Run Polars Engine
    return calculate_portfolio_consolidation(assets, transactions)
