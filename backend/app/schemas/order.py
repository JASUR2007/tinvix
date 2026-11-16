from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class OrderItemCreate(BaseModel):
    product_id: int
    title: str
    price: float
    quantity: int


class OrderItemResponse(OrderItemCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    items: List[OrderItemCreate]


class OrderResponse(BaseModel):
    id: int
    user_id: Optional[str]
    user_name: Optional[str]
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)
