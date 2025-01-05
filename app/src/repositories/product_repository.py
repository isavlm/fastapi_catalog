from abc import ABC, abstractmethod
from typing import List, Optional

from ..core.models import Product


class ProductRepository(ABC):
    @abstractmethod
    def create(self, product: Product) -> Product:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> List[Product]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, product_id: str) -> Optional[Product]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, product_id: str) -> Product:
        raise NotImplementedError

    @abstractmethod
    def filter(self, filter_by: str) -> List[Product]:
        return self.filter_by_status(filter_by)
        # raise NotImplementedError

    @abstractmethod
    def update(self, product_id: str,  product: Product) -> Product:
        raise NotImplementedError