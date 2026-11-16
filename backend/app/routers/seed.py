from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.product import Product
from app.routers.products import verify_admin

router = APIRouter(prefix="/seed", tags=["Seed"])

DEMO_ITEMS = [
    {
        "title": "Перфоратор Bosch GBH 2-26 DRE",
        "price": 12990.0,
        "description": "Трехрежимный перфоратор SDS-plus мощностью 800 Вт для тяжелых работ.",
        "image_url": "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=600&auto=format&fit=crop&q=80",
    },
    {
        "title": "Дрель-шуруповерт Makita DDF453",
        "price": 8490.0,
        "description": "Аккумуляторная дрель с двухскоростным редуктором и быстрозажимным патроном.",
        "image_url": "https://images.unsplash.com/photo-1572981779307-38b8cabb2407?w=600&auto=format&fit=crop&q=80",
    },
    {
        "title": "Лазерный нивелир ADA Cube 3D",
        "price": 6490.0,
        "description": "Компактный самовыравнивающийся лазерный уровень с яркими лучами 360 градусов.",
        "image_url": "https://images.unsplash.com/photo-1581783342308-f792dbdd27c5?w=600&auto=format&fit=crop&q=80",
    },
    {
        "title": "Набор инструментов Tinvix Pro 142",
        "price": 9990.0,
        "description": "Универсальный слесарный набор в ударопрочном кейсе из хромованадиевой стали.",
        "image_url": "https://images.unsplash.com/photo-1530124566582-a618bc2615dc?w=600&auto=format&fit=crop&q=80",
    },
]


@router.post("")
async def seed_demo_products(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_admin),
):
    result = await db.execute(select(Product))
    existing = result.scalars().all()
    if existing:
        return {"status": "ok", "message": "Товары уже есть в базе", "count": len(existing)}

    for item in DEMO_ITEMS:
        db.add(Product(**item))
    await db.commit()
    return {"status": "ok", "message": "Демо-товары успешно добавлены", "count": len(DEMO_ITEMS)}
