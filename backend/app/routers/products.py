from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.config import settings
from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse, ProductListResponse
from app.services.storage import storage_service

router = APIRouter(prefix="/products", tags=["Products"])


async def verify_admin(
    x_admin_secret: Optional[str] = Header(None, alias="X-Admin-Secret"),
):
    if not settings.ADMIN_API_KEY:
        return
    if not x_admin_secret or x_admin_secret != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён: требуется ключ администратора (заголовок X-Admin-Secret)",
        )


@router.get("", response_model=ProductListResponse)
async def list_products(
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    stmt = (
        select(Product)
        .order_by(desc(Product.created_at))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    products = result.scalars().all()

    # Total count
    count_stmt = select(Product)
    count_res = await db.execute(count_stmt)
    total = len(count_res.scalars().all())

    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден",
        )
    return ProductResponse.model_validate(product)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_admin),
):
    if payload.telegram_file_id:
        existing = await db.execute(
            select(Product).where(Product.telegram_file_id == payload.telegram_file_id)
        )
        found = existing.scalar_one_or_none()
        if found:
            return ProductResponse.model_validate(found)

    product = Product(
        title=payload.title.strip(),
        image_url=payload.image_url.strip(),
        price=payload.price,
        description=payload.description,
        telegram_file_id=payload.telegram_file_id,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return ProductResponse.model_validate(product)


@router.post("/upload", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product_with_file(
    title: str = Form(...),
    price: Optional[float] = Form(0.0),
    description: Optional[str] = Form(None),
    telegram_file_id: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_admin),
):
    # Idempotency check: if Telegram retries an update, avoid duplicate upload & DB record
    if telegram_file_id:
        existing = await db.execute(
            select(Product).where(Product.telegram_file_id == telegram_file_id)
        )
        found = existing.scalar_one_or_none()
        if found:
            return ProductResponse.model_validate(found)

    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Разрешены только изображения (JPEG, PNG, WebP и т.д.)",
        )

    file_bytes = await file.read()
    image_url = storage_service.upload_file(
        file_bytes=file_bytes,
        filename=file.filename or "image.jpg",
        content_type=file.content_type,
    )

    product = Product(
        title=title.strip(),
        image_url=image_url,
        price=price,
        description=description,
        telegram_file_id=telegram_file_id,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return ProductResponse.model_validate(product)
