from typing import Optional
from app.src.exceptions import ProductRepositoryException, ProductNotFoundException

from app.src.core.models import Product
from app.src.repositories import ProductRepository

from .request import FilterProductsByStatusRequest
from .response import FilterProductsByStatusResponse


class FilterProductByStatus:

    def __init__(self, product_repository: ProductRepository) -> None:
        self.product_repository = product_repository

    def __call__(self, request: FilterProductsByStatusRequest) -> FilterProductsByStatusResponse:
        try:
            # Get products with the requested status
            existing_products = self.product_repository.filter(request.status)
            
            # Return empty list if no products found
            if not existing_products:
                return FilterProductsByStatusResponse(products=[])
            
            # Return found products
            return FilterProductsByStatusResponse(products=existing_products)
        except ProductRepositoryException as e:
            raise e
        except Exception as e:
            raise ProductRepositoryException(method="filter", message=str(e))