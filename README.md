# Brazilian Financial Asset Consolidator (`fin_consolidator`)

High-precision, self-hosted financial asset consolidation platform built for Brazilian market realities (Ações B3, FIIs, Tesouro Direto, CDBs, Crypto, and Offshore).

## Tech Stack
- **Database**: PostgreSQL 16 (JSONB for multi-classification + Persistent Docker Volume)
- **Calculation Engine**: Polars (Multi-threaded Rust-accelerated dataframe engine for instant financial recalculations)
- **Backend API**: Python 3.12 + FastAPI + SQLAlchemy 2.0 (Async) + Pydantic v2
- **Infrastructure**: Docker & Docker Compose (2 basic containers: `fin_db` and `fin_api`)

---

## Getting Started

### 1. Start the Containers
```bash
docker compose up --build -d
```

### 2. Check Logs
```bash
docker compose logs -f api
```

### 3. Access Interactive API Documentation
Open your browser and navigate to:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## Core Endpoints

### 1. Assets (`/api/v1/assets`)
- `POST /api/v1/assets`: Register an asset (`id`, `name`, `type`, and JSONB `metadata_json`).
- `GET /api/v1/assets`: List assets (supports `?type=STOCK` or `?tag=Dividendos`).
- `GET /api/v1/assets/{id}`: Retrieve single asset.
- `PUT /api/v1/assets/{id}`: Update name, type, or metadata.
- `DELETE /api/v1/assets/{id}`: Delete asset.

### 2. Transactions (`/api/v1/transactions`)
- `POST /api/v1/transactions`: Register a transaction (`asset_id`, `type`, `trade_date`, `total_spent`, and JSONB `details`).
- `POST /api/v1/transactions/bulk`: Bulk insert transactions from broker notes or spreadsheets.
- `GET /api/v1/transactions`: List transactions with filters (`asset_id`, `type`, date range).
- `DELETE /api/v1/transactions/{id}`: Delete transaction.

### 3. Portfolio Consolidation (`/api/v1/portfolio/consolidation`)
- `GET /api/v1/portfolio/consolidation`: Runs the **Polars Calculation Engine** to compute:
  - Current quantities
  - Weighted Average Price (*Preço Médio*)
  - Total invested cost basis
  - Total dividends and JCP received
  - Portfolio allocation percentages by asset class
  - Returns the consolidated JSON tree.

---

## Persistence & Backups
- Database data is stored in the Docker volume `fin_pg_data`.
- Running `docker compose down` will safely stop the containers **without losing any data**.
- To create a quick SQL backup:
```bash
docker exec -t fin_db pg_dump -U fin_user fin_consolidator > storage/backup_$(date +%Y%m%d).sql
```
# fin_consolidator
