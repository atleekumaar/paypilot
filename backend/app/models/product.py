"""SQLAlchemy database models for products."""

from sqlalchemy import Column, String, Float, Integer, Boolean, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ProductModel(Base):
    """SQLAlchemy model representing a product in the database."""

    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    brand = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False, index=True)
    currency = Column(String, default="USD")
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    stock = Column(Boolean, default=True, index=True)
    seller = Column(String, nullable=False)
    delivery_days = Column(Integer, default=3)
    features = Column(JSON, default=dict)
    image_url = Column(String, nullable=True)

    def to_dict(self) -> dict:
        """Convert model instance to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "brand": self.brand,
            "category": self.category,
            "description": self.description,
            "price": self.price,
            "currency": self.currency,
            "rating": self.rating,
            "review_count": self.review_count,
            "stock": self.stock,
            "seller": self.seller,
            "delivery_days": self.delivery_days,
            "features": self.features or {},
            "image_url": self.image_url,
        }
