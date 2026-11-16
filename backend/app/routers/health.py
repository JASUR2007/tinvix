from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app.core.config import settings
from app.services.storage import storage_service

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    storage_ok, storage_detail = storage_service.check_health()
    is_healthy = (db_status == "ok") and storage_ok

    return {
        "status": "healthy" if is_healthy else "degraded",
        "instance_id": settings.INSTANCE_ID,
        "database": db_status,
        "minio": storage_detail,
        "storage_type": storage_service.storage_type,
    }
