from app.routers.products import router as products_router
from app.routers.orders import router as orders_router
from app.routers.health import router as health_router
from app.routers.seed import router as seed_router

__all__ = ["products_router", "orders_router", "health_router", "seed_router"]
