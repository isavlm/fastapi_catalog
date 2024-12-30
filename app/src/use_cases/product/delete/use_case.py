from typing import Optional

from app.src.exceptions import (
    ProductNotFoundException,
    ProductRepositoryException
)

from app.src.core.models import Product
from app.src.repositories import ProductRepository

from .request import DeleteProductRequest
from .response import DeleteProductResponse


class DeleteProduct:
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository

    def __call__(
        self, product_id: str, request: DeleteProductRequest
    ) -> Optional[DeleteProductResponse]:
        try:
            with self.product_repository.session() as session:
                existing_product = self.product_repository.get_by_id(
                    product_id, session=session
                )
                self.__verify_product_exists(
                    existing_product, request_entity_id=request.product_id
                )
                response = self.product_repository.delete(
                    product_id, session=session
                )
                return response
        except ProductNotFoundException as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ProductRepositoryException as e:
            raise HTTPException(status_code=500, detail=str(e))

    def __verify_product_exists(
        self, existing_product: Optional[Product], request_entity_id: str
    ) -> None:
        if existing_product is None:
            raise ProductNotFoundException(
                f"Product with ID {request_entity_id} not found"
            )