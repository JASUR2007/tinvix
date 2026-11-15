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

    minio_status = "ok"
    try:
        storage_service.client.bucket_exists(settings.MINIO_BUCKET)
    except Exception as e:
        minio_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "ok" and minio_status == "ok" else "degraded",
        "instance_id": settings.INSTANCE_ID,
        "database": db_status,
        "minio": minio_status,
    }
