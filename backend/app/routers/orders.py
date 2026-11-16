from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate,
    db: AsyncSession = Depends(get_db),
):
    if not payload.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заказ должен содержать хотя бы один товар",
        )

    total_amount = sum(item.price * item.quantity for item in payload.items)

    order = Order(
        user_id=payload.user_id,
        user_name=payload.user_name,
        total_amount=total_amount,
        status="created",
    )
    db.add(order)
    await db.flush()

    for item in payload.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            title=item.title,
            price=item.price,
            quantity=item.quantity,
        )
        db.add(order_item)

    await db.commit()
    await db.refresh(order)
    return OrderResponse.model_validate(order)


@router.get("", response_model=list[OrderResponse])
async def list_orders(
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
):
    stmt = select(Order).order_by(desc(Order.created_at)).limit(limit)
    result = await db.execute(stmt)
    orders = result.scalars().all()
    return [OrderResponse.model_validate(o) for o in orders]
