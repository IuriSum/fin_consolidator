"""
Unit & Domain Validation Tests for the FinConsolidator Backend:
1. Polars Calculation Engine & Multi-Asset Categorization.
2. Pydantic Stateless Contracts & Financial Math Discrepancy Detection.
3. Corporate Event & Type Validation.

ALL TESTS COMMENTED OUT — building prototype first.
"""

# from datetime import date
# from decimal import Decimal
# import uuid
# from pydantic import ValidationError
#
# from app.models.asset import Asset
# from app.models.transaction import Transaction
# from app.schemas.asset import AssetCreate
# from app.schemas.transaction import TransactionCreate
# from app.services.polars_engine import calculate_portfolio_consolidation
#
#
# def test_polars_consolidation_flow():
#     # 1. Create mock assets (ACOES and FII)
#     petr4 = Asset(
#         id="PETR4",
#         name="Petróleo Brasileiro S.A. - Petrobras",
#         type="ACOES",
#         metadata_json={
#             "currency": "BRL",
#             "sector": "Petróleo e Gás",
#             "tags": ["Commodities", "Dividendos", "Estatais"],
#             "target_allocation_pct": 10.0
#         }
#     )
#     hglg11 = Asset(
#         id="HGLG11",
#         name="CSHG Logística FII",
#         type="FII",
#         metadata_json={
#             "currency": "BRL",
#             "segment": "Logística",
#             "tags": ["Tijolo", "FII", "Renda Mensal"],
#             "target_allocation_pct": 15.0
#         }
#     )
#
#     assets = [petr4, hglg11]
#
#     # 2. Create mock transactions (BUY, DIVIDEND, SELL)
#     transactions = [
#         Transaction(
#             id=uuid.uuid4(),
#             asset_id="PETR4",
#             type="BUY",
#             trade_date=date(2024, 1, 10),
#             total_spent=Decimal("3005.0000"),
#             details={
#                 "quantity": 100.0,
#                 "unit_price": 30.0,
#                 "total_costs": 5.0,
#                 "broker": "XP"
#             }
#         ),
#         Transaction(
#             id=uuid.uuid4(),
#             asset_id="PETR4",
#             type="BUY",
#             trade_date=date(2024, 2, 10),
#             total_spent=Decimal("4005.0000"),
#             details={
#                 "quantity": 100.0,
#                 "unit_price": 40.0,
#                 "total_costs": 5.0,
#                 "broker": "XP"
#             }
#         ),
#         Transaction(
#             id=uuid.uuid4(),
#             asset_id="PETR4",
#             type="DIVIDEND",
#             trade_date=date(2024, 3, 15),
#             total_spent=Decimal("150.0000"),
#             details={
#                 "quantity": 100.0,
#                 "unit_price": 1.5,
#                 "total_costs": 0.0,
#                 "broker": "XP"
#             }
#         ),
#         Transaction(
#             id=uuid.uuid4(),
#             asset_id="PETR4",
#             type="SELL",
#             trade_date=date(2024, 4, 10),
#             total_spent=Decimal("2250.0000"),
#             details={
#                 "quantity": 50.0,
#                 "unit_price": 45.0,
#                 "total_costs": 2.5,
#                 "broker": "XP"
#             }
#         ),
#         Transaction(
#             id=uuid.uuid4(),
#             asset_id="HGLG11",
#             type="BUY",
#             trade_date=date(2024, 1, 15),
#             total_spent=Decimal("1600.0000"),
#             details={
#                 "quantity": 10.0,
#                 "unit_price": 160.0,
#                 "total_costs": 0.0,
#                 "broker": "BTG"
#             }
#         ),
#         Transaction(
#             id=uuid.uuid4(),
#             asset_id="HGLG11",
#             type="DIVIDEND",
#             trade_date=date(2024, 2, 15),
#             total_spent=Decimal("11.0000"),
#             details={
#                 "quantity": 10.0,
#                 "unit_price": 1.1,
#                 "total_costs": 0.0,
#                 "broker": "BTG"
#             }
#         ),
#     ]
#
#     result = calculate_portfolio_consolidation(assets, transactions)
#
#     print("--- CONSOLIDATION RESULTS ---")
#     print(f"Total Invested: R$ {result.total_portfolio_invested}")
#     print(f"Total Dividends: R$ {result.total_portfolio_dividends}")
#     print(f"By Asset Type: {result.by_type}")
#     for p in result.positions:
#         print(f"Position: {p.asset_id} | Type: {p.type} | Qty: {p.current_quantity} | PM: R$ {p.average_price} | Invested: R$ {p.total_invested}")
#
#     # Assertions
#     petr4_pos = next(p for p in result.positions if p.asset_id == "PETR4")
#     assert petr4_pos.name == "Petróleo Brasileiro S.A. - Petrobras"
#     assert petr4_pos.type == "ACOES"
#     assert petr4_pos.current_quantity == Decimal("150.00000000")
#     assert petr4_pos.average_price == Decimal("35.0500")
#     assert petr4_pos.total_dividends_received == Decimal("150.00")
#
#     hglg_pos = next(p for p in result.positions if p.asset_id == "HGLG11")
#     assert hglg_pos.name == "CSHG Logística FII"
#     assert hglg_pos.type == "FII"
#     assert hglg_pos.current_quantity == Decimal("10.00000000")
#     assert hglg_pos.average_price == Decimal("160.0000")
#     assert hglg_pos.total_dividends_received == Decimal("11.00")
#
#     print("\n✅ Polars math & position assertions passed!")
#
#
# def test_stateless_pydantic_validators():
#     print("\n--- TESTING STATELESS PYDANTIC VALIDATORS ---")
#
#     # 1. Invalid Asset Type rejection
#     try:
#         AssetCreate(
#             id="INVALID1",
#             name="Invalid Asset",
#             type="NOT_A_VALID_TYPE"
#         )
#         assert False, "Should have rejected invalid asset type!"
#     except ValidationError as e:
#         print("✅ Correctly rejected invalid asset type:", e.errors()[0]["msg"])
#
#     # 2. Financial Math Discrepancy rejection
#     try:
#         TransactionCreate(
#             asset_id="PETR4",
#             type="BUY",
#             trade_date=date(2026, 1, 15),
#             total_spent=Decimal("5000.00"),  # Expected: 100 * 30 + 5 = 3005.00
#             details={"quantity": 100, "unit_price": 30.00, "total_costs": 5.00}
#         )
#         assert False, "Should have rejected financial math discrepancy!"
#     except ValidationError as e:
#         print("✅ Correctly rejected financial math discrepancy:", e.errors()[0]["msg"])
#
#     # 3. Split with non-zero total_spent rejection
#     try:
#         TransactionCreate(
#             asset_id="PETR4",
#             type="SPLIT",
#             trade_date=date(2026, 1, 15),
#             total_spent=Decimal("100.00"),  # Expected: 0
#             details={"quantity": 100}
#         )
#         assert False, "Should have rejected split with non-zero total_spent!"
#     except ValidationError as e:
#         print("✅ Correctly rejected corporate event non-zero cost:", e.errors()[0]["msg"])
#
#     print("✅ All Stateless Pydantic validation tests passed!")
#
#
# if __name__ == "__main__":
#     test_polars_consolidation_flow()
#     test_stateless_pydantic_validators()
