from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
import polars as pl
from app.models.asset import Asset
from app.models.transaction import Transaction
from app.schemas.consolidation import AssetPosition, PortfolioConsolidationResponse


def calculate_portfolio_consolidation(
    assets: List[Asset],
    transactions: List[Transaction]
) -> PortfolioConsolidationResponse:
    """
    High-performance portfolio consolidation using Polars.
    Computes current positions, Preço Médio (Weighted Average Price),
    accumulated income, and category breakdowns.
    """
    if not assets:
        return PortfolioConsolidationResponse(
            consolidated_at=datetime.utcnow(),
            total_portfolio_invested=Decimal("0.00"),
            total_portfolio_dividends=Decimal("0.00"),
            total_portfolio_jcp=Decimal("0.00"),
            total_assets_count=0,
            by_asset_type={},
            positions=[],
        )

    # 1. Map assets by ID for quick metadata retrieval
    asset_map: Dict[str, Asset] = {a.id: a for a in assets}

    if not transactions:
        # Assets exist but have no transactions yet
        empty_positions = [
            AssetPosition(
                asset_id=a.id,
                asset_type=a.asset_type,
                currency=a.currency,
                metadata=a.metadata_json or {},
                current_quantity=Decimal("0.00000000"),
                average_price=Decimal("0.0000"),
                total_invested=Decimal("0.00"),
                total_costs_paid=Decimal("0.00"),
                total_dividends_received=Decimal("0.00"),
                total_jcp_received=Decimal("0.00"),
                total_transactions=0,
                last_trade_date=None,
            )
            for a in assets
        ]
        return PortfolioConsolidationResponse(
            consolidated_at=datetime.utcnow(),
            total_portfolio_invested=Decimal("0.00"),
            total_portfolio_dividends=Decimal("0.00"),
            total_portfolio_jcp=Decimal("0.00"),
            total_assets_count=len(assets),
            by_asset_type={},
            positions=empty_positions,
        )

    # 2. Build Polars DataFrame from transactions
    tx_data = [
        {
            "id": str(t.id),
            "asset_id": t.asset_id,
            "trade_date": t.trade_date.isoformat(),
            "operation_type": str(t.operation_type).upper(),
            "quantity": float(t.quantity),
            "unit_price": float(t.unit_price),
            "total_costs": float(t.total_costs),
            "broker": t.broker or "",
        }
        for t in transactions
    ]

    df = pl.DataFrame(tx_data)
    
    # Sort chronologically by date
    df = df.sort(["trade_date", "id"])

    # 3. Calculate position state per asset
    positions: List[AssetPosition] = []
    
    # Group transactions by asset
    unique_assets = df["asset_id"].unique().to_list()
    
    total_port_invested = Decimal("0.00")
    total_port_dividends = Decimal("0.00")
    total_port_jcp = Decimal("0.00")

    for asset_id in asset_map.keys():
        asset_obj = asset_map[asset_id]
        asset_txs = df.filter(pl.col("asset_id") == asset_id)

        if asset_txs.height == 0:
            positions.append(
                AssetPosition(
                    asset_id=asset_obj.id,
                    asset_type=asset_obj.asset_type,
                    currency=asset_obj.currency,
                    metadata=asset_obj.metadata_json or {},
                    current_quantity=Decimal("0.00000000"),
                    average_price=Decimal("0.0000"),
                    total_invested=Decimal("0.00"),
                    total_costs_paid=Decimal("0.00"),
                    total_dividends_received=Decimal("0.00"),
                    total_jcp_received=Decimal("0.00"),
                    total_transactions=0,
                    last_trade_date=None,
                )
            )
            continue

        # Iterate over chronologically sorted operations for this asset
        current_qty = Decimal("0")
        total_cost_basis = Decimal("0")
        total_costs_paid = Decimal("0")
        total_dividends = Decimal("0")
        total_jcp = Decimal("0")
        last_date = None

        rows = asset_txs.iter_rows(named=True)
        for r in rows:
            op = r["operation_type"]
            q = Decimal(str(r["quantity"]))
            p = Decimal(str(r["unit_price"]))
            c = Decimal(str(r["total_costs"]))
            last_date = r["trade_date"]
            total_costs_paid += c

            if op in ["BUY", "SUBSCRIPTION"]:
                trade_total = (q * p) + c
                total_cost_basis += trade_total
                current_qty += q
            elif op == "SELL":
                if current_qty > 0:
                    avg_price = total_cost_basis / current_qty
                    # Reduce cost basis proportionally
                    total_cost_basis -= (q * avg_price)
                    current_qty -= q
                    if current_qty <= 0:
                        current_qty = Decimal("0")
                        total_cost_basis = Decimal("0")
            elif op == "DIVIDEND":
                total_dividends += (q * p)
            elif op == "JCP":
                total_jcp += (q * p)
            elif op in ["SPLIT", "BONUS"]:
                # Split adds shares without increasing cost basis
                current_qty += q
            elif op == "AMORTIZATION":
                # Amortization directly reduces cost basis
                total_cost_basis -= (q * p)
                if total_cost_basis < 0:
                    total_cost_basis = Decimal("0")

        avg_price = (total_cost_basis / current_qty) if current_qty > 0 else Decimal("0.0000")
        
        pos = AssetPosition(
            asset_id=asset_obj.id,
            asset_type=asset_obj.asset_type,
            currency=asset_obj.currency,
            metadata=asset_obj.metadata_json or {},
            current_quantity=round(current_qty, 8),
            average_price=round(avg_price, 4),
            total_invested=round(total_cost_basis, 2),
            total_costs_paid=round(total_costs_paid, 2),
            total_dividends_received=round(total_dividends, 2),
            total_jcp_received=round(total_jcp, 2),
            total_transactions=asset_txs.height,
            last_trade_date=last_date,
        )
        positions.append(pos)
        
        total_port_invested += pos.total_invested
        total_port_dividends += pos.total_dividends_received
        total_port_jcp += pos.total_jcp_received

    # 4. Summary by Asset Type
    by_asset_type: Dict[str, Dict[str, Any]] = {}
    for pos in positions:
        atype = pos.asset_type
        if atype not in by_asset_type:
            by_asset_type[atype] = {
                "total_invested": Decimal("0.00"),
                "total_dividends": Decimal("0.00"),
                "total_jcp": Decimal("0.00"),
                "asset_count": 0,
                "allocation_pct": Decimal("0.00"),
            }
        by_asset_type[atype]["total_invested"] += pos.total_invested
        by_asset_type[atype]["total_dividends"] += pos.total_dividends_received
        by_asset_type[atype]["total_jcp"] += pos.total_jcp_received
        by_asset_type[atype]["asset_count"] += 1

    # Compute allocation percentages
    for atype, data in by_asset_type.items():
        if total_port_invested > 0:
            data["allocation_pct"] = round((data["total_invested"] / total_port_invested) * Decimal("100.0"), 2)
        else:
            data["allocation_pct"] = Decimal("0.00")

    return PortfolioConsolidationResponse(
        consolidated_at=datetime.utcnow(),
        total_portfolio_invested=round(total_port_invested, 2),
        total_portfolio_dividends=round(total_portfolio_dividends, 2),
        total_portfolio_jcp=round(total_port_jcp, 2),
        total_assets_count=len(assets),
        by_asset_type=by_asset_type,
        positions=positions,
    )
