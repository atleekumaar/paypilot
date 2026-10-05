"""Repository interfaces and implementations for PayPilot."""

from abc import ABC, abstractmethod
import json
from pathlib import Path
from typing import List, Optional

from app.schemas.product import Product

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "products.json"


class ProductRepository(ABC):
    """Abstract interface defining the product repository contracts."""

    @abstractmethod
    def get_by_id(self, product_id: str) -> Optional[Product]:
        """Fetch a single product by unique SKU identifier."""
        pass

    @abstractmethod
    def list_products(
        self,
        category: Optional[str] = None,
        in_stock_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Product]:
        """List products with optional category and stock filtering."""
        pass

    @abstractmethod
    def search(
        self,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        in_stock_only: bool = True,
        keywords: Optional[List[str]] = None,
    ) -> List[Product]:
        """Perform deterministic filtered search over product collection."""
        pass

    @abstractmethod
    def update_stock(self, product_id: str, stock: bool) -> bool:
        """Update inventory stock availability."""
        pass


class DemoProductRepository(ProductRepository):
    """In-memory demo implementation loaded from deterministic JSON catalogue."""

    def __init__(self, data_file: Path = DATA_PATH):
        self._data_file = data_file
        self._products: List[Product] = []
        self._load_data()

    def _load_data(self) -> None:
        if self._data_file.exists():
            with open(self._data_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                self._products = [Product.model_validate(item) for item in raw_data]
        else:
            self._products = []

    def get_by_id(self, product_id: str) -> Optional[Product]:
        normalized_id = product_id.strip().upper()
        for prod in self._products:
            if prod.id.upper() == normalized_id:
                return prod
        return None

    def list_products(
        self,
        category: Optional[str] = None,
        in_stock_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Product]:
        results = self._products
        if category:
            cat_norm = category.strip().lower()
            results = [p for p in results if p.category.lower() == cat_norm]
        if in_stock_only:
            results = [p for p in results if p.stock]
        return results[offset : offset + limit]

    def search(
        self,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        in_stock_only: bool = True,
        keywords: Optional[List[str]] = None,
    ) -> List[Product]:
        candidates = self._products

        # Category constraint
        if category:
            cat_norm = category.strip().lower().rstrip("s")  # handle plural/singular
            candidates = [p for p in candidates if p.category.lower().rstrip("s") == cat_norm]

        # Stock constraint (Strict Rule: Out of stock must never be recommended)
        if in_stock_only:
            candidates = [p for p in candidates if p.stock]

        # Hard Price constraints (Strict Rule: Over budget must never be included)
        if min_price is not None:
            candidates = [p for p in candidates if p.price >= min_price]
        if max_price is not None:
            candidates = [p for p in candidates if p.price <= max_price]

        # Minimum Rating constraint
        if min_rating is not None:
            candidates = [p for p in candidates if p.rating >= min_rating]

        # Keyword relevance
        if keywords:
            cleaned_keywords = [k.lower().strip() for k in keywords if k.strip()]
            if cleaned_keywords:
                matched: List[Product] = []
                for p in candidates:
                    text_blob = f"{p.name} {p.brand} {p.category} {p.description} {json.dumps(p.features)}".lower()
                    # Include if at least one meaningful keyword matches or partial match
                    if any(k in text_blob for k in cleaned_keywords):
                        matched.append(p)
                candidates = matched

        return candidates

    def update_stock(self, product_id: str, stock: bool) -> bool:
        normalized_id = product_id.strip().upper()
        for i, prod in enumerate(self._products):
            if prod.id.upper() == normalized_id:
                updated_prod = prod.model_copy(update={"stock": stock})
                self._products[i] = updated_prod
                return True
        return False


class SQLAlchemyProductRepository(ProductRepository):
    """PostgreSQL-ready SQLAlchemy repository implementation."""

    def __init__(self, session):
        self.session = session

    def get_by_id(self, product_id: str) -> Optional[Product]:
        from app.models.product import ProductModel
        obj = self.session.query(ProductModel).filter(ProductModel.id == product_id).first()
        return Product.model_validate(obj) if obj else None

    def list_products(
        self,
        category: Optional[str] = None,
        in_stock_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Product]:
        from app.models.product import ProductModel
        query = self.session.query(ProductModel)
        if category:
            query = query.filter(ProductModel.category == category.lower())
        if in_stock_only:
            query = query.filter(ProductModel.stock == True)
        results = query.offset(offset).limit(limit).all()
        return [Product.model_validate(r) for r in results]

    def search(
        self,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        in_stock_only: bool = True,
        keywords: Optional[List[str]] = None,
    ) -> List[Product]:
        from app.models.product import ProductModel
        query = self.session.query(ProductModel)
        if category:
            query = query.filter(ProductModel.category == category.lower())
        if in_stock_only:
            query = query.filter(ProductModel.stock == True)
        if min_price is not None:
            query = query.filter(ProductModel.price >= min_price)
        if max_price is not None:
            query = query.filter(ProductModel.price <= max_price)
        if min_rating is not None:
            query = query.filter(ProductModel.rating >= min_rating)
        results = query.all()
        return [Product.model_validate(r) for r in results]

    def update_stock(self, product_id: str, stock: bool) -> bool:
        from app.models.product import ProductModel
        obj = self.session.query(ProductModel).filter(ProductModel.id == product_id).first()
        if obj:
            obj.stock = stock
            self.session.commit()
            return True
        return False


# Singleton demo repository instance for dependency injection
_demo_repo_instance: Optional[DemoProductRepository] = None


def get_product_repository() -> ProductRepository:
    """Dependency provider returning the product repository instance."""
    global _demo_repo_instance
    if _demo_repo_instance is None:
        _demo_repo_instance = DemoProductRepository()
    return _demo_repo_instance
