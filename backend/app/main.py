import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database import init_db
from app.services.storage import storage_service
from app.routers import products_router, orders_router, health_router, seed_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("tinvix-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables...")
    try:
        await init_db()
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error("Failed to initialize database tables: %s", e)

    logger.info("Ensuring MinIO bucket...")
    try:
        storage_service.ensure_bucket()
        logger.info("MinIO bucket ensured successfully.")
    except Exception as e:
        logger.warning("Could not ensure MinIO bucket on startup: %s", e)

    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Stateless Product Catalog API with PostgreSQL and MinIO",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router, prefix="/api")
app.include_router(orders_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.include_router(seed_router, prefix="/api")
app.include_router(health_router, prefix="")


@app.get("/")
async def root():
    return {
        "service": settings.APP_NAME,
        "instance_id": settings.INSTANCE_ID,
        "docs": "/docs",
        "endpoints": {
            "catalog": "/api/products",
            "orders": "/api/orders",
            "health": "/api/health",
        },
    }
