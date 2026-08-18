# Domain Architecture & Business Rules Documentation

This document defines the core domain specifications, data contracts, and business rules for the financial asset consolidation platform.

---

## 1. Asset Domain Rules

### 1.1 Identification & Naming Rule
* **Name Requirement**: Every asset must have a `name` (String, max 150 chars).
* **Ticker vs Descriptive Name**:
  * Not all financial assets have a market ticker (e.g., private fixed income, OTC instruments, cash reserves).
  * If the asset is an exchange-traded stock or fund (`ACOES`, `FII`, `FIAGRO`, `FIINFRA`, `ETF`), the `name` column **must contain the ticker** (e.g., `PETR4`, `HGLG11`, `KCRE11`, `JURO11`, `BOVA11`).
  * For non-ticker assets (`TESOURO`, `RENDA_FIXA`, `CRIPTO`, `OTHER`), the `name` column stores the descriptive product name (e.g., `Tesouro Selic 2029`, `CDB Banco Inter 120% CDI`).
* **Company Legal Entity**:
  * The issuer / company legal name is stored inside `metadata_json["company"]` (e.g., `Petróleo Brasileiro S.A. - Petrobras`, `Banco do Brasil S.A.`).

### 1.2 Asset Types Standard
The system enforces strict asset classification via `STANDARD_ASSET_TYPES`:
* `ACOES`: Equities / Common and Preferred stocks traded on B3 (ON, PN, UNIT).
* `FII`: Real Estate Investment Funds (*Fundos de Investimento Imobiliário*).
* `FIAGRO`: Agro-industrial Credit and Land Funds (*Fundos Agro*).
* `FIINFRA`: Infrastructure Investment Funds (*Incentivados - Lei 12.431*).
* `RENDA_FIXA`: Private fixed income (CDB, LCI, LCA, CRI, CRA, Debêntures).
* `TESOURO`: Brazilian Treasury bonds (*Tesouro Direto* - Selic, IPCA+, Prefixado).
* `ETF`: Exchange Traded Funds (e.g., `BOVA11`, `SMAL11`, `IVVB11`, `HASH11`).
* `FUNDO`: Traditional mutual funds with platform custody (*Multimercado, FIA, FIRF*).
* `CRIPTO`: Cryptocurrency and digital assets (*BTC, ETH, SOL*).
* `OTHER`: Custom assets, private equity notes, or alternative investments.

### 1.3 Asset JSONB Metadata Contract
The `metadata_json` field on the `assets` table follows this standard schema:
```json
{
  "company": "Banco do Brasil S.A.",
  "cnpj": "00.000.000/0001-91",
  "quantity": 286.00,
  "medium_price": 21.81
}
```
