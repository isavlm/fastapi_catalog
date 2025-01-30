from typing import List
from decimal import Decimal
from pydantic import BaseModel, validator
from app.src.core.enums._product_statuses import ProductStatuses

"""After the issue with the update method,I added a validator to check if the product_id only accepts numbers.
So now the user can only use numbers in the product_id.
""" 

class ProductBase(BaseModel):
    product_id: str
    user_id: str
    name: str
    description: str
    price: Decimal
    location: str
    status: str
    is_available: bool

# Isadora's code here.
# Adding validator to check if the product_id only accepts numbers and to check if the status is in lowercase or uppercase. 


    @validator('product_id')
    def validate_product_id(cls, v):
        if not v.isdigit():
            raise ValueError("product_id should be numbers only")
        return v

    @validator('status')
    def validate_status(cls, v):
        if v.lower() not in [s.value.lower() for s in ProductStatuses]:
            raise ValueError(f"status must be one of: {', '.join([s.value for s in ProductStatuses])}")
        return v.title()  # Normalize status to title case


class ListProductResponseDto(BaseModel):
    products: List[ProductBase]


class FindProductByIdResponseDto(ProductBase):
    ...


class CreateProductRequestDto(ProductBase):
    ...


class CreateProductResponseDto(ProductBase):
    ...

#Isadora's code starts here.
class DeleteProductResponse(BaseModel):
    ...


class DeleteProductRequest(BaseModel):
    product_id: str

    @validator('product_id')
    def validate_product_id(cls, v):
        if not v.isdigit():
            raise ValueError("product_id should be numbers only")
        return v


class UpdateProductResponseDto(ProductBase):
    ...

class UpdateProductRequestDto(ProductBase):
    @validator('product_id')
    def validate_product_id(cls, v):
        if not v.isdigit():
            raise ValueError("product_id should be numbers only")
        return v

class FilterProductsByStatusRequestDto(BaseModel):
    status: str

    @validator('status')
    def validate_status(cls, v):
        try:
            status_value = next(
                status for status in ProductStatuses
                if status.value.lower() == v.lower()
            )
            return status_value.value
        except StopIteration:
            valid_values = [status.value for status in ProductStatuses]
            raise ValueError(f"Not a valid status value. Must be one of: {', '.join(valid_values)}")

class FilterProductByStatusResponseDto(BaseModel):
    products: List[ProductBase]

# Isadora's code ends here.