from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate


class AssetService:
    @staticmethod
    async def list_assets(
        db: AsyncSession,
        type: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[Asset]:
        query = select(Asset).order_by(Asset.id.asc())
        if type:
            query = query.where(Asset.type == type.strip().upper())
        
        result = await db.execute(query)
        assets = result.scalars().all()
        
        if tag:
            assets = [
                a for a in assets 
                if a.metadata_json and tag in a.metadata_json.get("tags", [])
            ]
        return assets

    @staticmethod
    async def get_asset_by_id(db: AsyncSession, asset_id: str) -> Asset:
        asset_id_norm = asset_id.strip().upper()
        asset = await db.get(Asset, asset_id_norm)
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset '{asset_id_norm}' not found."
            )
        return asset

    @staticmethod
    async def create_asset(db: AsyncSession, asset_in: AssetCreate) -> Asset:
        asset_id_norm = asset_in.id.strip().upper()
        existing = await db.get(Asset, asset_id_norm)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Asset with ticker/ID '{asset_id_norm}' already exists."
            )

        asset = Asset(
            id=asset_id_norm,
            name=asset_in.name.strip(),
            type=asset_in.type.strip().upper(),
            metadata_json=asset_in.metadata_json or {},
        )
        db.add(asset)
        await db.commit()
        await db.refresh(asset)
        return asset

    @staticmethod
    async def update_asset(db: AsyncSession, asset_id: str, asset_in: AssetUpdate) -> Asset:
        asset = await AssetService.get_asset_by_id(db, asset_id)

        if asset_in.name is not None:
            asset.name = asset_in.name.strip()
        if asset_in.type is not None:
            asset.type = asset_in.type.strip().upper()
        if asset_in.metadata_json is not None:
            asset.metadata_json = asset_in.metadata_json

        await db.commit()
        await db.refresh(asset)
        return asset

    @staticmethod
    async def delete_asset(db: AsyncSession, asset_id: str) -> None:
        asset = await AssetService.get_asset_by_id(db, asset_id)
        await db.delete(asset)
        await db.commit()
