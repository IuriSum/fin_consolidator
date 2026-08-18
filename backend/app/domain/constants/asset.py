"""
Standard Asset Types and Classification Constants for Brazilian Financial Assets.
"""
from enum import Enum
from typing import List, Dict


class AssetType(str, Enum):
    ACOES = "ACOES"
    FII = "FII"
    FIAGRO = "FIAGRO"
    FIINFRA = "FIINFRA"
    RENDA_FIXA = "RENDA_FIXA"
    TESOURO = "TESOURO"
    ETF = "ETF"
    FUNDO = "FUNDO"
    CRIPTO = "CRIPTO"
    OTHER = "OTHER"


# Standard List of valid asset types
STANDARD_ASSET_TYPES: List[str] = [
    AssetType.ACOES.value,
    AssetType.FII.value,
    AssetType.FIAGRO.value,
    AssetType.FIINFRA.value,
    AssetType.RENDA_FIXA.value,
    AssetType.TESOURO.value,
    AssetType.ETF.value,
    AssetType.FUNDO.value,
    AssetType.CRIPTO.value,
    AssetType.OTHER.value,
]


# Human-friendly descriptions / titles
ASSET_TYPE_LABELS: Dict[str, str] = {
    AssetType.ACOES.value: "Ações (B3)",
    AssetType.FII.value: "Fundos de Investimento Imobiliário (FII)",
    AssetType.FIAGRO.value: "Fundos nas Cadeias Produtivas Agroindustriais (FIAGRO)",
    AssetType.FIINFRA.value: "Fundos de Infraestrutura Incentivados (FI-INFRA)",
    AssetType.RENDA_FIXA.value: "Renda Fixa Privada (CDB, LCI, LCA, CRI, CRA, Debêntures)",
    AssetType.TESOURO.value: "Tesouro Direto (Selic, IPCA+, Prefixado)",
    AssetType.ETF.value: "Fundos de Índice (Exchange Traded Funds)",
    AssetType.FUNDO.value: "Fundos de Investimento Tradicionais (Multimercado, FIA, FIRF)",
    AssetType.CRIPTO.value: "Criptoativos (Bitcoin, Ethereum, etc.)",
    AssetType.OTHER.value: "Outros Ativos / Personalizados",
}
