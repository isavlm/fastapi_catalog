from typing import List
from decimal import Decimal
from pydantic import BaseModel, field_validator
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


    @field_validator('product_id')
    def validate_product_id(cls, v):
        if not v.isdigit():
            raise ValueError("product_id should be numbers only")
        return v

    @field_validator('status')
    def validate_status(cls, v):
        if v.lower() not in [s.value.lower() for s in ProductStatuses]:
            raise ValueError(f"status must be one of: {', '.join([s.value for s in ProductStatuses])}")
        # Return the exact enum value instead of title case
        for status in ProductStatuses:
            if v.lower() == status.value.lower():
                return status.value
        return v


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


class DeleteProductRequestDto(BaseModel):
    product_id: str

    @field_validator('product_id')
    def validate_product_id(cls, v):
        if not v.isdigit():
            raise ValueError("product_id should be numbers only")
        return v


class UpdateProductResponseDto(ProductBase):
    ...

class UpdateProductRequestDto(ProductBase):
    @field_validator('product_id')
    def validate_product_id(cls, v):
        if not v.isdigit():
            raise ValueError("product_id should be numbers only")
        return v

class FilterProductsByStatusRequestDto(BaseModel):
    status: str

    @field_validator('status')
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