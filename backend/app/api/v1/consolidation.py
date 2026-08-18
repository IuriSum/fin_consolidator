from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.consolidation import (
    PortfolioConsolidationResponse,
    ConsolidationCreate,
    ConsolidationUpdate,
    ConsolidationResponse,
)
from app.services.consolidation_service import ConsolidationService

router = APIRouter(tags=["Portfolio Consolidation"])


@router.get("/portfolio/consolidation", response_model=PortfolioConsolidationResponse)
async def get_portfolio_consolidation(db: AsyncSession = Depends(get_db)):
    """
    Executes the high-performance Polars calculation engine
    over the entire transactional ledger and returns the
    consolidated multi-classified JSON portfolio state.
    """
    return await ConsolidationService.get_portfolio_consolidation(db=db)


# --- Consolidations History & Snapshots API ---

@router.post("/consolidations", response_model=ConsolidationResponse, status_code=status.HTTP_201_CREATED)
async def create_consolidation_snapshot(
    consolidation_in: ConsolidationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Saves a consolidated portfolio snapshot (JSONB) into the database.
    """
    return await ConsolidationService.create_snapshot(db=db, consolidation_in=consolidation_in)


@router.get("/consolidations", response_model=List[ConsolidationResponse])
async def list_consolidations(
    year: Optional[int] = Query(None, description="Filter by reference year"),
    type: Optional[str] = Query(None, description="Filter by consolidation type (ANNUAL, MONTHLY, etc.)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lists saved consolidation snapshots.
    """
    return await ConsolidationService.list_snapshots(db=db, year=year, type=type)


@router.get("/consolidations/{consolidation_id}", response_model=ConsolidationResponse)
async def get_consolidation_snapshot(
    consolidation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves a specific consolidation snapshot by ID.
    """
    return await ConsolidationService.get_snapshot_by_id(db=db, consolidation_id=consolidation_id)


@router.put("/consolidations/{consolidation_id}", response_model=ConsolidationResponse)
async def update_consolidation_snapshot(
    consolidation_id: uuid.UUID,
    consolidation_in: ConsolidationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Updates an existing consolidation snapshot.
    """
    return await ConsolidationService.update_snapshot(
        db=db,
        consolidation_id=consolidation_id,
        consolidation_in=consolidation_in
    )


@router.delete("/consolidations/{consolidation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_consolidation_snapshot(
    consolidation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Deletes a consolidation snapshot.
    """
    await ConsolidationService.delete_snapshot(db=db, consolidation_id=consolidation_id)
    return None
