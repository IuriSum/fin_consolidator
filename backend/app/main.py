from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
import app.models  # Ensure all SQLAlchemy models are registered in Base.metadata
from app.api.v1.assets import router as assets_router
from app.api.v1.transactions import router as transactions_router
from app.api.v1.consolidation import router as consolidation_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="High-precision Brazilian Financial Asset Consolidator API with PostgreSQL and Polars",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Routers
app.include_router(assets_router, prefix="/api/v1")
app.include_router(transactions_router, prefix="/api/v1")
app.include_router(consolidation_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Financial Consolidator API is operational",
        "docs": "/docs",
        "version": "0.1.1"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
