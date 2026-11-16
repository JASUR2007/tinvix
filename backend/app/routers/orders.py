from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderResponse
from app.core.config import settings

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate, db: AsyncSession = Depends(get_db)):
    if not payload.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Заказ должен содержать товары")

    product_ids = [item.product_id for item in payload.items]
    p_stmt = select(Product).where(Product.id.in_(product_ids))
    p_res = await db.execute(p_stmt)
    catalog = {p.id: p for p in p_res.scalars().all()}

    # Calculate authoritative prices from server database
    order_items_data = []
    total_amount = 0.0
    for item in payload.items:
        db_p = catalog.get(item.product_id)
        price = float(db_p.price) if db_p and db_p.price else float(item.price)
        title = db_p.title if db_p else item.title
        total_amount += price * item.quantity
        order_items_data.append({"product_id": item.product_id, "title": title, "price": price, "quantity": item.quantity})

    order = Order(
        user_id=payload.user_id,
        user_name=payload.user_name,
        total_amount=total_amount,
        status="created",
    )
    db.add(order)
    await db.flush()

    for item_data in order_items_data:
        db.add(OrderItem(order_id=order.id, **item_data))

    await db.commit()
    await db.refresh(order)
    return OrderResponse.model_validate(order)


@router.get("", response_model=list[OrderResponse])
async def list_orders(
    user_id: Optional[str] = None,
    x_admin_secret: Optional[str] = Header(None, alias="X-Admin-Secret"),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
):
    is_admin = bool(settings.ADMIN_API_KEY and x_admin_secret == settings.ADMIN_API_KEY)
    if not is_admin and not user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Просмотр всех заказов требует прав администратора",
        )

    stmt = select(Order).order_by(desc(Order.created_at)).limit(limit)
    if not is_admin and user_id:
        stmt = stmt.where(Order.user_id == user_id)

    result = await db.execute(stmt)
    return [OrderResponse.model_validate(o) for o in result.scalars().all()]
