from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate, AssetResponse

router = APIRouter(prefix="/assets", tags=["Assets"])


@router.get("", response_model=List[AssetResponse])
async def list_assets(
    asset_type: Optional[str] = Query(None, description="Filter by asset class (STOCK, FII, etc.)"),
    tag: Optional[str] = Query(None, description="Filter assets containing a specific tag in JSONB metadata"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Asset)
    if asset_type:
        query = query.where(Asset.asset_type == asset_type.upper())
    
    result = await db.execute(query)
    assets = result.scalars().all()
    
    if tag:
        # Filter in Python / JSONB
        assets = [
            a for a in assets 
            if a.metadata_json and tag in a.metadata_json.get("tags", [])
        ]
    return assets


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(asset_in: AssetCreate, db: AsyncSession = Depends(get_db)):
    asset_id_normalized = asset_in.id.strip().upper()
    existing = await db.get(Asset, asset_id_normalized)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Asset with ID '{asset_id_normalized}' already exists."
        )

    asset = Asset(
        id=asset_id_normalized,
        name=asset_in.name.strip() if asset_in.name else None,
        asset_type=asset_in.asset_type.strip().upper(),
        currency=asset_in.currency.strip().upper(),
        metadata_json=asset_in.metadata_json or {},
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: str, db: AsyncSession = Depends(get_db)):
    asset = await db.get(Asset, asset_id.strip().upper())
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Asset '{asset_id}' not found.")
    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(asset_id: str, asset_in: AssetUpdate, db: AsyncSession = Depends(get_db)):
    asset = await db.get(Asset, asset_id.strip().upper())
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Asset '{asset_id}' not found.")

    if asset_in.name is not None:
        asset.name = asset_in.name.strip() if asset_in.name else None
    if asset_in.asset_type is not None:
        asset.asset_type = asset_in.asset_type.strip().upper()
    if asset_in.currency is not None:
        asset.currency = asset_in.currency.strip().upper()
    if asset_in.metadata_json is not None:
        # Merge or replace metadata JSON
        asset.metadata_json = asset_in.metadata_json

    await db.commit()
    await db.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(asset_id: str, db: AsyncSession = Depends(get_db)):
    asset = await db.get(Asset, asset_id.strip().upper())
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Asset '{asset_id}' not found.")
    
    await db.delete(asset)
    await db.commit()
    return None
