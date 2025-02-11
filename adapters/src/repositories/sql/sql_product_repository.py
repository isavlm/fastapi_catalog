from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from app.src import Product, ProductRepository, ProductRepositoryException
from app.src.core.enums._product_statuses import ProductStatuses
from .tables import ProductSchema
from app.src.exceptions import ProductNotFoundException

class SQLProductRepository(ProductRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> List[Product]:
        try:
            with self.session as session:
                products = session.query(ProductSchema).all()
                if products is None:
                    return []
                product_list = [
                    Product(
                        product_id=str(product.product_id),
                        user_id=str(product.user_id),
                        name=str(product.name),
                        description=str(product.description),
                        price=Decimal(product.price),
                        location=str(product.location),
                        status=product.status,
                        is_available=bool(product.is_available),
                    )
                    for product in products
                ]
                return product_list
        except Exception:
            self.session.rollback()
            raise ProductRepositoryException(method="list")

    def create(self, product: Product) -> Product:
        try:
            product_to_create = ProductSchema(
                product_id=product.product_id,
                user_id=product.user_id,
                name=product.name,
                description=product.description,
                price=product.price,
                location=product.location,
                status=product.status,
                is_available=product.is_available,
            )
            with self.session as session:
                session.add(product_to_create)
                session.commit()
            return product
        except Exception:
            self.session.rollback()
            raise ProductRepositoryException(method="create")

    def get_by_id(self, product_id: str) -> Optional[Product]:
        try:
            with self.session as session:
                product = (
                    session.query(ProductSchema)
                    .filter(ProductSchema.product_id == product_id)
                    .first()
                )
                if product is None:
                    return None
                return Product(
                    product_id=str(product.product_id),
                    user_id=str(product.user_id),
                    name=str(product.name),
                    description=str(product.description),
                    price=Decimal(product.price),
                    location=str(product.location),
                    status=product.status,
                    is_available=bool(product.is_available),
                )
        except Exception:
            self.session.rollback()
            raise ProductRepositoryException(method="find")

    def update(self, product: Product) -> Product:
        try:
            with self.session as session:
                existing_product = (session.query(ProductSchema).filter(
                    ProductSchema.product_id == product.product_id).first())
                
                if existing_product is None:
                    raise ProductRepositoryException(
                        method="edit", message="Product not found")
                
                existing_product.user_id = product.user_id
                existing_product.name = product.name
                existing_product.description = product.description
                existing_product.price = product.price
                existing_product.location = product.location
                existing_product.status = product.status
                existing_product.is_available = product.is_available
                
                session.commit()

            print(f"Product updated successfully: {product}")
            return product
        except Exception as e:
            self.session.rollback()
            print(f"Error occurred: {str(e)}")
            raise ProductRepositoryException(method="update", message=str(e))

    def delete(self, product_id: str) -> Optional[Product]:
        try:
            with self.session as session:
                product = (
                    session.query(ProductSchema)
                    .filter(ProductSchema.product_id == product_id)
                    .first()
                )
                if product is None:
                    raise ProductRepositoryException(
                        method="delete", message="Product not found"
                    )
                session.query(ProductSchema).filter(
                    ProductSchema.product_id == product_id).delete()
                session.commit()
                return Product(
                    product_id=str(product.product_id),
                    user_id=str(product.user_id),
                    name=str(product.name),
                    description=str(product.description),
                    price=Decimal(product.price),
                    location=str(product.location),
                    status=product.status,
                    is_available=bool(product.is_available),
                )
        except Exception:
            self.session.rollback()
            raise ProductRepositoryException(method="delete")
        
    def filter(self, status: ProductStatuses) -> List[Product]:
        try:
            with self.session as session:
                # Query to filter products by status and return a list of results
                products = session.query(ProductSchema).filter(ProductSchema.status == status.value).all()

                if not products:
                    print(f"No products found with status: {status.value}")
                    return []

                # Return the list of products converted to Product model
                return [
                    Product(
                        product_id=str(product.product_id),
                        user_id=str(product.user_id),
                        name=str(product.name),
                        description=str(product.description),
                        price=Decimal(product.price),
                        location=str(product.location),
                        status=product.status,
                        is_available=bool(product.is_available),
                        )
                        for product in products
                    ]
        except Exception:
            self.session.rollback()
            raise ProductRepositoryException(method="get_by_status")