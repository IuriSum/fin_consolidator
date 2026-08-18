from typing import List, Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.asset import Asset
from app.models.transaction import Transaction
from app.models.consolidation import Consolidation
from app.schemas.consolidation import (
    PortfolioConsolidationResponse,
    ConsolidationCreate,
    ConsolidationUpdate,
)
from app.services.polars_engine import calculate_portfolio_consolidation


class ConsolidationService:
    @staticmethod
    async def get_portfolio_consolidation(db: AsyncSession) -> PortfolioConsolidationResponse:
        """
        Executes the high-performance Polars calculation engine
        over the entire transactional ledger and returns the
        consolidated multi-classified JSON portfolio state.
        """
        # Fetch all assets
        assets_result = await db.execute(select(Asset).order_by(Asset.id.asc()))
        assets = assets_result.scalars().all()

        # Fetch all transactions ordered chronologically
        tx_result = await db.execute(
            select(Transaction).order_by(Transaction.trade_date.asc(), Transaction.created_at.asc())
        )
        transactions = tx_result.scalars().all()

        # Run Polars Engine
        return calculate_portfolio_consolidation(assets, transactions)

    @staticmethod
    async def create_snapshot(
        db: AsyncSession,
        consolidation_in: ConsolidationCreate
    ) -> Consolidation:
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

    @staticmethod
    async def list_snapshots(
        db: AsyncSession,
        year: Optional[int] = None,
        type: Optional[str] = None
    ) -> List[Consolidation]:
        query = select(Consolidation).order_by(Consolidation.year.desc(), Consolidation.version.desc())
        if year is not None:
            query = query.where(Consolidation.year == year)
        if type:
            query = query.where(Consolidation.type == type.strip().upper())

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_snapshot_by_id(
        db: AsyncSession,
        consolidation_id: uuid.UUID
    ) -> Consolidation:
        snapshot = await db.get(Consolidation, consolidation_id)
        if not snapshot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Consolidation snapshot '{consolidation_id}' not found."
            )
        return snapshot

    @staticmethod
    async def update_snapshot(
        db: AsyncSession,
        consolidation_id: uuid.UUID,
        consolidation_in: ConsolidationUpdate
    ) -> Consolidation:
        snapshot = await ConsolidationService.get_snapshot_by_id(db, consolidation_id)

        if consolidation_in.type is not None:
            snapshot.type = consolidation_in.type.strip().upper()
        if consolidation_in.year is not None:
            snapshot.year = consolidation_in.year
        if consolidation_in.version is not None:
            snapshot.version = consolidation_in.version
        if consolidation_in.data is not None:
            snapshot.data = consolidation_in.data

        await db.commit()
        await db.refresh(snapshot)
        return snapshot

    @staticmethod
    async def delete_snapshot(
        db: AsyncSession,
        consolidation_id: uuid.UUID
    ) -> None:
        snapshot = await ConsolidationService.get_snapshot_by_id(db, consolidation_id)
        await db.delete(snapshot)
        await db.commit()
