from typing import Optional

from app.src.exceptions import (
    ProductNotFoundException,
    ProductRepositoryException
)
from fastapi.exceptions import HTTPException
from app.src.core.models import Product
from app.src.repositories import ProductRepository

from .request import DeleteProductRequest
from .response import DeleteProductResponse


class DeleteProduct:
    def __init__(self, product_repository):
        self.product_repository = product_repository

    def __call__(self, request: DeleteProductRequest) -> Optional[DeleteProductResponse]:
        try:
            with self.product_repository.session() as session:
                existing_product = self.product_repository.get_by_id(
                    request.product_id, session=session
                )
                self.__verify_product_exists(
                    existing_product, request_entity_id=request.product_id
                )
                response = self.product_repository.delete(
                    request.product_id, session=session
                )
                return response
        except ProductNotFoundException as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ProductRepositoryException as e:
            raise HTTPException(status_code=500, detail=str(e))