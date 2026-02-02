from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .config import settings
from .database import init_db
from .scheduler import start_scheduler, stop_scheduler
from .api import funds, holdings, nav, pnl, transactions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting up Fund Tracker API...")
    init_db()  # Initialize database tables
    start_scheduler()  # Start scheduler
    yield
    # Shutdown
    logger.info("Shutting down Fund Tracker API...")
    stop_scheduler()


# Create FastAPI app
app = FastAPI(
    title="Fund Tracker API",
    description="中国基金实时净收益查询系统",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(funds.router)
app.include_router(holdings.router)
app.include_router(nav.router)
app.include_router(pnl.router)
app.include_router(transactions.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Fund Tracker API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
