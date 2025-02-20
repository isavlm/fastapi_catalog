from .base import RepositoryException


class ProductRepositoryException(RepositoryException):
    def __init__(self, method: str, message: str = None):
        super().__init__(entity_type="Product", method=method, message=message)
