from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    image_url = Column(String(1024), nullable=False)
    price = Column(Numeric(10, 2), nullable=True, default=0.0)
    description = Column(Text, nullable=True)
    telegram_file_id = Column(String(255), unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
