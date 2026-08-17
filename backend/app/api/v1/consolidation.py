import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.asset import Asset
from app.models.transaction import Transaction
from app.models.consolidation import Consolidation
from app.schemas.consolidation import (
    PortfolioConsolidationResponse,
    ConsolidationCreate,
    ConsolidationUpdate,
    ConsolidationResponse,
)
from app.services.polars_engine import calculate_portfolio_consolidation

router = APIRouter(tags=["Portfolio Consolidation"])


@router.get("/portfolio/consolidation", response_model=PortfolioConsolidationResponse)
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


# --- Consolidations History & Snapshots API ---

@router.post("/consolidations", response_model=ConsolidationResponse, status_code=status.HTTP_201_CREATED)
async def create_consolidation_snapshot(
    consolidation_in: ConsolidationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Saves a consolidated portfolio snapshot (JSONB) into the database.
    """
    consolidation = Consolidation(
        type=consolidation_in.type.strip().upper(),
        year=consolidation_in.year,
        version=consolidation_in.version,
        data=consolidation_in.data or {},
    )
    db.add(consolidation)
    await db.commit()
    await db.refresh(consolidation)
    return consolidation


@router.get("/consolidations", response_model=List[ConsolidationResponse])
async def list_consolidations(
    year: Optional[int] = Query(None, description="Filter by reference year"),
    type: Optional[str] = Query(None, description="Filter by consolidation type (ANNUAL, MONTHLY, etc.)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lists saved consolidation snapshots.
    """
    query = select(Consolidation).order_by(Consolidation.year.desc(), Consolidation.version.desc())
    if year is not None:
        query = query.where(Consolidation.year == year)
    if type:
        query = query.where(Consolidation.type == type.strip().upper())

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/consolidations/{consolidation_id}", response_model=ConsolidationResponse)
async def get_consolidation_snapshot(
    consolidation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves a specific consolidation snapshot by ID.
    """
    consolidation = await db.get(Consolidation, consolidation_id)
    if not consolidation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consolidation snapshot '{consolidation_id}' not found."
        )
    return consolidation


@router.put("/consolidations/{consolidation_id}", response_model=ConsolidationResponse)
async def update_consolidation_snapshot(
    consolidation_id: uuid.UUID,
    consolidation_in: ConsolidationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Updates a consolidation snapshot.
    """
    consolidation = await db.get(Consolidation, consolidation_id)
    if not consolidation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consolidation snapshot '{consolidation_id}' not found."
        )

    if consolidation_in.type is not None:
        consolidation.type = consolidation_in.type.strip().upper()
    if consolidation_in.year is not None:
        consolidation.year = consolidation_in.year
    if consolidation_in.version is not None:
        consolidation.version = consolidation_in.version
    if consolidation_in.data is not None:
        consolidation.data = consolidation_in.data

    await db.commit()
    await db.refresh(consolidation)
    return consolidation


@router.delete("/consolidations/{consolidation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_consolidation_snapshot(
    consolidation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Deletes a consolidation snapshot.
    """
    consolidation = await db.get(Consolidation, consolidation_id)
    if not consolidation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consolidation snapshot '{consolidation_id}' not found."
        )
    await db.delete(consolidation)
    await db.commit()
    return None
