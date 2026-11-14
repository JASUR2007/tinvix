from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    title: str
    price: Optional[float] = 0.0
    description: Optional[str] = None


class ProductCreate(ProductBase):
    image_url: str
    telegram_file_id: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    image_url: str
    telegram_file_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
