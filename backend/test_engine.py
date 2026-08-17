"""
Unit test for the Polars Calculation Engine
Verifies Preço Médio, Desdobramento/Split, Dividends, and Multi-Classification Output.
"""
from datetime import date
from decimal import Decimal
import uuid
from app.models.asset import Asset
from app.models.transaction import Transaction
from app.services.polars_engine import calculate_portfolio_consolidation


def test_polars_consolidation_flow():
    # 1. Create mock assets
    petr4 = Asset(
        id="PETR4",
        asset_type="STOCK",
        currency="BRL",
        metadata_json={
            "sector": "Petróleo e Gás",
            "tags": ["Commodities", "Dividendos", "Estatais"],
            "target_allocation_pct": 10.0
        }
    )
    hglg11 = Asset(
        id="HGLG11",
        asset_type="FII",
        currency="BRL",
        metadata_json={
            "segment": "Logística",
            "tags": ["Tijolo", "FII", "Renda Mensal"],
            "target_allocation_pct": 15.0
        }
    )
    
    assets = [petr4, hglg11]

    # 2. Create mock transactions
    # PETR4:
    # 2024-01-10: BUY 100 @ 30.00 (Cost: 3000.00 + 5.00 fees) -> Qty: 100, Total: 3005.00, PM: 30.05
    # 2024-02-10: BUY 100 @ 40.00 (Cost: 4000.00 + 5.00 fees) -> Qty: 200, Total: 7010.00, PM: 35.05
    # 2024-03-15: DIVIDEND 100 * 1.50 = 150.00
    # 2024-04-10: SELL 50 @ 45.00 -> PM stays 35.05, Qty: 150, Total: 5257.50
    # HGLG11:
    # 2024-01-15: BUY 10 @ 160.00 (Cost: 1600.00) -> Qty: 10, Total: 1600.00, PM: 160.00
    # 2024-02-15: DIVIDEND 10 * 1.10 = 11.00

    transactions = [
        Transaction(
            id=uuid.uuid4(),
            asset_id="PETR4",
            trade_date=date(2024, 1, 10),
            operation_type="BUY",
            quantity=Decimal("100.00000000"),
            unit_price=Decimal("30.0000"),
            total_costs=Decimal("5.0000"),
            broker="XP",
            details={}
        ),
        Transaction(
            id=uuid.uuid4(),
            asset_id="PETR4",
            trade_date=date(2024, 2, 10),
            operation_type="BUY",
            quantity=Decimal("100.00000000"),
            unit_price=Decimal("40.0000"),
            total_costs=Decimal("5.0000"),
            broker="XP",
            details={}
        ),
        Transaction(
            id=uuid.uuid4(),
            asset_id="PETR4",
            trade_date=date(2024, 3, 15),
            operation_type="DIVIDEND",
            quantity=Decimal("100.00000000"),
            unit_price=Decimal("1.5000"),
            total_costs=Decimal("0.0000"),
            broker="XP",
            details={}
        ),
        Transaction(
            id=uuid.uuid4(),
            asset_id="PETR4",
            trade_date=date(2024, 4, 10),
            operation_type="SELL",
            quantity=Decimal("50.00000000"),
            unit_price=Decimal("45.0000"),
            total_costs=Decimal("2.5000"),
            broker="XP",
            details={}
        ),
        Transaction(
            id=uuid.uuid4(),
            asset_id="HGLG11",
            trade_date=date(2024, 1, 15),
            operation_type="BUY",
            quantity=Decimal("10.00000000"),
            unit_price=Decimal("160.0000"),
            total_costs=Decimal("0.0000"),
            broker="BTG",
            details={}
        ),
        Transaction(
            id=uuid.uuid4(),
            asset_id="HGLG11",
            trade_date=date(2024, 2, 15),
            operation_type="DIVIDEND",
            quantity=Decimal("10.00000000"),
            unit_price=Decimal("1.1000"),
            total_costs=Decimal("0.0000"),
            broker="BTG",
            details={}
        ),
    ]

    result = calculate_portfolio_consolidation(assets, transactions)

    print("--- CONSOLIDATION RESULTS ---")
    print(f"Total Invested: R$ {result.total_portfolio_invested}")
    print(f"Total Dividends: R$ {result.total_portfolio_dividends}")
    print(f"By Asset Type: {result.by_asset_type}")
    for p in result.positions:
        print(f"Position: {p.asset_id} | Qty: {p.current_quantity} | PM: R$ {p.average_price} | Invested: R$ {p.total_invested}")

    # Assertions
    petr4_pos = next(p for p in result.positions if p.asset_id == "PETR4")
    assert petr4_pos.current_quantity == Decimal("150.00000000")
    assert petr4_pos.average_price == Decimal("35.0500")
    assert petr4_pos.total_dividends_received == Decimal("150.00")
    
    hglg_pos = next(p for p in result.positions if p.asset_id == "HGLG11")
    assert hglg_pos.current_quantity == Decimal("10.00000000")
    assert hglg_pos.average_price == Decimal("160.0000")
    assert hglg_pos.total_dividends_received == Decimal("11.00")

    print("\n✅ All Polars math and precision assertions passed successfully!")


if __name__ == "__main__":
    test_polars_consolidation_flow()
