from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.asset import AssetCreate, AssetUpdate, AssetResponse
from app.services.asset_service import AssetService

router = APIRouter(prefix="/assets", tags=["Assets"])


@router.get("", response_model=List[AssetResponse])
async def list_assets(
    type: Optional[str] = Query(None, description="Filter by standard asset type (ACOES, FII, etc.)"),
    tag: Optional[str] = Query(None, description="Filter assets containing a specific tag in JSONB metadata"),
    db: AsyncSession = Depends(get_db)
):
    return await AssetService.list_assets(db=db, type=type, tag=tag)


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(asset_in: AssetCreate, db: AsyncSession = Depends(get_db)):
    return await AssetService.create_asset(db=db, asset_in=asset_in)


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: int, db: AsyncSession = Depends(get_db)):
    return await AssetService.get_asset_by_id(db=db, asset_id=asset_id)


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(asset_id: int, asset_in: AssetUpdate, db: AsyncSession = Depends(get_db)):
    return await AssetService.update_asset(db=db, asset_id=asset_id, asset_in=asset_in)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(asset_id: int, db: AsyncSession = Depends(get_db)):
    await AssetService.delete_asset(db=db, asset_id=asset_id)
    return None
