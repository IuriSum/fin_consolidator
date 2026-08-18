from datetime import date
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.transaction import (
    TransactionCreate,
    TransactionBulkCreate,
    TransactionResponse,
)
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=List[TransactionResponse])
async def list_transactions(
    asset_id: Optional[int] = Query(None, description="Filter by asset integer ID"),
    type: Optional[str] = Query(None, description="Filter by transaction operation type (BUY, SELL, OTHER, etc.)"),
    start_date: Optional[date] = Query(None, description="Filter from date (inclusive)"),
    end_date: Optional[date] = Query(None, description="Filter up to date (inclusive)"),
    db: AsyncSession = Depends(get_db)
):
    return await TransactionService.list_transactions(
        db=db,
        asset_id=asset_id,
        type=type,
        start_date=start_date,
        end_date=end_date
    )


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(tx_in: TransactionCreate, db: AsyncSession = Depends(get_db)):
    return await TransactionService.create_transaction(db=db, tx_in=tx_in)


@router.post("/bulk", response_model=List[TransactionResponse], status_code=status.HTTP_201_CREATED)
async def create_transactions_bulk(
    bulk_in: TransactionBulkCreate,
    db: AsyncSession = Depends(get_db)
):
    return await TransactionService.create_transactions_bulk(db=db, bulk_in=bulk_in)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(transaction_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await TransactionService.delete_transaction(db=db, transaction_id=transaction_id)
    return None
