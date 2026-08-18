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
    Asset types are resolved from the Asset model.
    """
    if not assets:
        return PortfolioConsolidationResponse(
            consolidated_at=datetime.utcnow(),
            total_portfolio_invested=Decimal("0.00"),
            total_portfolio_dividends=Decimal("0.00"),
            total_portfolio_jcp=Decimal("0.00"),
            total_assets_count=0,
            by_type={},
            positions=[],
        )

    # 1. Map assets by ID for quick metadata retrieval
    asset_map: Dict[int, Asset] = {a.id: a for a in assets}

    if not transactions:
        # Assets exist but have no transactions yet
        empty_positions = [
            AssetPosition(
                asset_id=a.id,
                name=a.name,
                type=a.type,
                currency=a.metadata_json.get("currency", "BRL") if a.metadata_json else "BRL",
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
            by_type={},
            positions=empty_positions,
        )

    # 2. Build Polars DataFrame from transactions (operation type from t.type, details from JSONB)
    tx_data = []
    for t in transactions:
        det = t.details or {}
        qty = float(det.get("quantity", 0.0))
        unit_price = float(det.get("unit_price", 0.0))
        total_costs = float(det.get("total_costs", 0.0))
        total_spent = float(t.total_spent)
        op = str(t.type).upper()
        
        # If unit_price wasn't explicit, infer from total_spent / qty
        if unit_price == 0.0 and qty > 0 and total_spent > 0:
            unit_price = total_spent / qty

        tx_data.append({
            "id": str(t.id),
            "asset_id": t.asset_id,
            "trade_date": t.trade_date.isoformat(),
            "total_spent": total_spent,
            "operation_type": op,
            "quantity": qty,
            "unit_price": unit_price,
            "total_costs": total_costs,
            "broker": str(det.get("broker", "")),
        })

    df = pl.DataFrame(tx_data)
    
    # Sort chronologically by date
    df = df.sort(["trade_date", "id"])

    # 3. Calculate position state per asset
    positions: List[AssetPosition] = []
    
    total_port_invested = Decimal("0.00")
    total_port_dividends = Decimal("0.00")
    total_port_jcp = Decimal("0.00")

    for asset_id in asset_map.keys():
        asset_obj = asset_map[asset_id]
        asset_txs = df.filter(pl.col("asset_id") == asset_id)
        currency = asset_obj.metadata_json.get("currency", "BRL") if asset_obj.metadata_json else "BRL"

        if asset_txs.height == 0:
            positions.append(
                AssetPosition(
                    asset_id=asset_obj.id,
                    name=asset_obj.name,
                    type=asset_obj.type,
                    currency=currency,
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
            spent = Decimal(str(r["total_spent"]))
            last_date = r["trade_date"]
            total_costs_paid += c

            if op in ["BUY", "SUBSCRIPTION"]:
                trade_total = spent if spent > 0 else (q * p) + c
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
                div_amount = spent if spent > 0 else (q * p)
                total_dividends += div_amount
            elif op == "JCP":
                jcp_amount = spent if spent > 0 else (q * p)
                total_jcp += jcp_amount
            elif op in ["SPLIT", "BONUS"]:
                # Split adds shares without increasing cost basis
                current_qty += q
            elif op == "AMORTIZATION":
                # Amortization directly reduces cost basis
                amort_amount = spent if spent > 0 else (q * p)
                total_cost_basis -= amort_amount
                if total_cost_basis < 0:
                    total_cost_basis = Decimal("0")
            elif op == "OTHER":
                # General other operations (non-position impacting unless specified)
                pass

        avg_price = (total_cost_basis / current_qty) if current_qty > 0 else Decimal("0.0000")
        
        pos = AssetPosition(
            asset_id=asset_obj.id,
            name=asset_obj.name,
            type=asset_obj.type,
            currency=currency,
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
    by_type: Dict[str, Dict[str, Any]] = {}
    for pos in positions:
        atype = pos.type
        if atype not in by_type:
            by_type[atype] = {
                "total_invested": Decimal("0.00"),
                "total_dividends": Decimal("0.00"),
                "total_jcp": Decimal("0.00"),
                "asset_count": 0,
                "allocation_pct": Decimal("0.00"),
            }
        by_type[atype]["total_invested"] += pos.total_invested
        by_type[atype]["total_dividends"] += pos.total_dividends_received
        by_type[atype]["total_jcp"] += pos.total_jcp_received
        by_type[atype]["asset_count"] += 1

    # Compute allocation percentages
    for atype, data in by_type.items():
        if total_port_invested > 0:
            data["allocation_pct"] = round((data["total_invested"] / total_port_invested) * Decimal("100.0"), 2)
        else:
            data["allocation_pct"] = Decimal("0.00")

    return PortfolioConsolidationResponse(
        consolidated_at=datetime.utcnow(),
        total_portfolio_invested=round(total_port_invested, 2),
        total_portfolio_dividends=round(total_port_dividends, 2),
        total_portfolio_jcp=round(total_port_jcp, 2),
        total_assets_count=len(assets),
        by_type=by_type,
        positions=positions,
    )
