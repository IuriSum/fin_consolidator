import uuid
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.asset import Asset
from app.models.transaction import Transaction
from app.schemas.transaction import (
    TransactionCreate,
    TransactionBulkCreate,
    TransactionResponse,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=List[TransactionResponse])
async def list_transactions(
    asset_id: Optional[str] = Query(None, description="Filter by asset ticker"),
    operation_type: Optional[str] = Query(None, description="Filter by operation type (BUY, SELL, etc.)"),
    start_date: Optional[date] = Query(None, description="Filter from date (inclusive)"),
    end_date: Optional[date] = Query(None, description="Filter up to date (inclusive)"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Transaction).order_by(Transaction.trade_date.desc(), Transaction.created_at.desc())
    
    if asset_id:
        query = query.where(Transaction.asset_id == asset_id.strip().upper())
    if operation_type:
        query = query.where(Transaction.operation_type == operation_type.upper())
    if start_date:
        query = query.where(Transaction.trade_date >= start_date)
    if end_date:
        query = query.where(Transaction.trade_date <= end_date)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(tx_in: TransactionCreate, db: AsyncSession = Depends(get_db)):
    asset_id_norm = tx_in.asset_id.strip().upper()
    asset = await db.get(Asset, asset_id_norm)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset '{asset_id_norm}' does not exist. Please register the asset first."
        )

    tx = Transaction(
        asset_id=asset_id_norm,
        trade_date=tx_in.trade_date,
        operation_type=tx_in.operation_type.value,
        quantity=tx_in.quantity,
        unit_price=tx_in.unit_price,
        total_costs=tx_in.total_costs,
        broker=tx_in.broker,
        details=tx_in.details or {},
    )
    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return tx


@router.post("/bulk", response_model=List[TransactionResponse], status_code=status.HTTP_201_CREATED)
async def create_transactions_bulk(
    bulk_in: TransactionBulkCreate,
    db: AsyncSession = Depends(get_db)
):
    # Verify all assets exist
    asset_ids = {t.asset_id.strip().upper() for t in bulk_in.transactions}
    existing_assets_result = await db.execute(select(Asset.id).where(Asset.id.in_(asset_ids)))
    existing_asset_ids = set(existing_assets_result.scalars().all())
    
    missing_assets = asset_ids - existing_asset_ids
    if missing_assets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The following assets do not exist: {list(missing_assets)}. Please create them before adding transactions."
        )

    tx_objects = [
        Transaction(
            asset_id=t.asset_id.strip().upper(),
            trade_date=t.trade_date,
            operation_type=t.operation_type.value,
            quantity=t.quantity,
            unit_price=t.unit_price,
            total_costs=t.total_costs,
            broker=t.broker,
            details=t.details or {},
        )
        for t in bulk_in.transactions
    ]
    
    db.add_all(tx_objects)
    await db.commit()
    for tx in tx_objects:
        await db.refresh(tx)
    return tx_objects


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(transaction_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    tx = await db.get(Transaction, transaction_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")
    
    await db.delete(tx)
    await db.commit()
    return None
