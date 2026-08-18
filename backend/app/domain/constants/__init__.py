"""Domain constants: strict asset classification and consolidation JSONB templates."""
from app.domain.constants.asset import (
    AssetType,
    STANDARD_ASSET_TYPES,
    ASSET_TYPE_LABELS,
)
from app.domain.constants.consolidation import (
    EMPTY_CONSOLIDATION_DATA_TEMPLATE,
    SAMPLE_CONSOLIDATION_DATA,
)

__all__ = [
    "AssetType",
    "STANDARD_ASSET_TYPES",
    "ASSET_TYPE_LABELS",
    "EMPTY_CONSOLIDATION_DATA_TEMPLATE",
    "SAMPLE_CONSOLIDATION_DATA",
]
