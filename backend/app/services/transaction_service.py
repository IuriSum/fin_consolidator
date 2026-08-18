from datetime import date
from decimal import Decimal
from typing import List, Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.asset import Asset
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionBulkCreate


class TransactionService:
    @staticmethod
    async def validate_sell_inventory(
        db: AsyncSession,
        asset_id: str,
        trade_date: date,
        sell_quantity: Decimal
    ) -> None:
        """
        Stateful Validation: Ensures user cannot sell more shares than
        accumulated in ledger history up to the transaction date.
        """
        query = select(Transaction).where(
            Transaction.asset_id == asset_id,
            Transaction.trade_date <= trade_date
        ).order_by(Transaction.trade_date.asc(), Transaction.created_at.asc())
        
        result = await db.execute(query)
        historical_txs = result.scalars().all()

        current_qty = Decimal("0")
        for tx in historical_txs:
            details = tx.details or {}
            qty = Decimal(str(details.get("quantity", "0")))
            op = tx.type.upper()

            if op in ["BUY", "SUBSCRIPTION", "SPLIT", "BONUS"]:
                current_qty += qty
            elif op == "SELL":
                current_qty -= qty

        if sell_quantity > current_qty:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Insufficient inventory for asset '{asset_id}': "
                    f"Attempting to SELL {sell_quantity}, but current available "
                    f"balance is {current_qty} as of {trade_date}."
                )
            )

    @staticmethod
    async def list_transactions(
        db: AsyncSession,
        asset_id: Optional[str] = None,
        type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Transaction]:
        query = select(Transaction).order_by(Transaction.trade_date.desc(), Transaction.created_at.desc())
        
        if asset_id:
            query = query.where(Transaction.asset_id == asset_id.strip().upper())
        if type:
            query = query.where(Transaction.type == type.strip().upper())
        if start_date:
            query = query.where(Transaction.trade_date >= start_date)
        if end_date:
            query = query.where(Transaction.trade_date <= end_date)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create_transaction(db: AsyncSession, tx_in: TransactionCreate) -> Transaction:
        asset_id_norm = tx_in.asset_id.strip().upper()
        asset = await db.get(Asset, asset_id_norm)
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset '{asset_id_norm}' does not exist. Please register the asset before adding transactions."
            )

        # Stateful validation: check inventory on SELL operations
        if tx_in.type.upper() == "SELL":
            sell_qty = Decimal(str(tx_in.details.get("quantity", "0")))
            if sell_qty > Decimal("0"):
                await TransactionService.validate_sell_inventory(
                    db=db,
                    asset_id=asset_id_norm,
                    trade_date=tx_in.trade_date,
                    sell_quantity=sell_qty
                )

        tx = Transaction(
            asset_id=asset_id_norm,
            type=tx_in.type.strip().upper(),
            trade_date=tx_in.trade_date,
            total_spent=tx_in.total_spent,
            details=tx_in.details or {},
        )
        db.add(tx)
        await db.commit()
        await db.refresh(tx)
        return tx

    @staticmethod
    async def create_transactions_bulk(
        db: AsyncSession,
        bulk_in: TransactionBulkCreate
    ) -> List[Transaction]:
        # 1. Verify all target assets exist
        asset_ids = {t.asset_id.strip().upper() for t in bulk_in.transactions}
        existing_assets_result = await db.execute(select(Asset.id).where(Asset.id.in_(asset_ids)))
        existing_asset_ids = set(existing_assets_result.scalars().all())
        
        missing_assets = asset_ids - existing_asset_ids
        if missing_assets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The following assets do not exist: {sorted(list(missing_assets))}. Please register them first."
            )

        # 2. Sort transactions chronologically for batch processing
        sorted_txs = sorted(bulk_in.transactions, key=lambda x: x.trade_date)

        # 3. Create transaction entities
        tx_objects = [
            Transaction(
                asset_id=t.asset_id.strip().upper(),
                type=t.type.strip().upper(),
                trade_date=t.trade_date,
                total_spent=t.total_spent,
                details=t.details or {},
            )
            for t in sorted_txs
        ]
        
        db.add_all(tx_objects)
        await db.commit()
        for tx in tx_objects:
            await db.refresh(tx)
        return tx_objects

    @staticmethod
    async def delete_transaction(db: AsyncSession, transaction_id: uuid.UUID) -> None:
        tx = await db.get(Transaction, transaction_id)
        if not tx:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found."
            )
        await db.delete(tx)
        await db.commit()
