from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
import logging

from api.src.dtos import (
    CreateProductRequestDto,
    UpdateProductRequestDto,
    DeleteProductRequestDto,
    DeleteProductResponse,
    FilterProductsByStatusRequestDto,
    ListProductResponseDto,
    CreateProductResponseDto,
    FindProductByIdResponseDto,
    UpdateProductResponseDto,
    FilterProductByStatusResponseDto,
    ProductBase
)

from app.src.use_cases.product import (
    ListProductResponse,
    FindProductByIdResponse,
    CreateProductResponse,
    UpdateProductResponse,
    FilterProductsByStatusResponse,
    ListProducts,
    FindProductById,
    CreateProduct,
    DeleteProduct,
    UpdateProduct,
    FilterProductByStatus,
    DeleteProductResponse,
    FindProductByIdRequest,
    CreateProductRequest,
    DeleteProductRequest,
    UpdateProductRequest,
    FilterProductsByStatusRequest,
)

from app.src.core.enums._product_statuses import ProductStatuses
from app.src.core.models import Product
from app.src.exceptions import ProductNotFoundException, ProductRepositoryException
from factories.use_cases.product import (
    get_product_repository,
    list_product_use_case,
    find_product_by_id_use_case,
    create_product_use_case,
    delete_product_use_case,
    update_product_use_case,
    filter_product_use_case
)
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

product_router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Product not found"}}
)


@product_router.get(
    "/",
    response_model=ListProductResponseDto,
    summary="List All Products",
    description="""
    Retrieve a list of all products in the catalog.
    
    Returns:
    - A list of products with their details including ID, name, price, status, and availability
    - An empty list if no products are found
    
    Optional Query Parameters:
    - location: Filter by store location
    - is_available: Filter by availability status (true/false)
    """
)
async def get_products(
    use_case: ListProducts = Depends(list_product_use_case),
) -> ListProductResponseDto:
    response = use_case()
    return ListProductResponseDto(
        products=[ProductBase(
            product_id=str(product.product_id),
            user_id=product.user_id,
            name=product.name,
            description=product.description,
            price=product.price,
            location=product.location,
            status=product.status.value,
            is_available=product.is_available
        ) for product in response.products]
    )


@product_router.get(
    "/filter-by-status",
    response_model=FilterProductByStatusResponseDto,
    summary="Filter Products by Status",
    description="""
    Filter products by their status (New, Used, or For parts).
    
    Parameters:
    - status_param: The status to filter by (New, Used, For parts)
    
    Returns:
    - A list of products matching the specified status
    - An empty list if no products match the status
    
    Example:
    ```
    GET /products/filter-by-status?status_param=New
    GET /products/filter-by-status?status_param=Used
    GET /products/filter-by-status?status_param=For parts
    ```
    """
)
async def filter_product_by_status(
    status_param: str,
    use_case: FilterProductByStatus = Depends(filter_product_use_case)
) -> FilterProductByStatusResponseDto:
    try:
        # Convert status_param to request object with enum value
        request = FilterProductsByStatusRequest(status=ProductStatuses(status_param))
        
        # Call use case with the request object
        response = use_case(request)
        
        # Convert the response to FilterProductByStatusResponseDto
        return FilterProductByStatusResponseDto(
            products=[
                ProductBase(
                    product_id=str(product.product_id),
                    user_id=product.user_id,
                    name=product.name,
                    description=product.description,
                    price=product.price,
                    location=product.location,
                    status=product.status.value,
                    is_available=product.is_available
                )
                for product in response.products
            ]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid status"
        )
    except Exception as e:
        logging.error(f"Error filtering products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@product_router.get(
    "/{product_id}",
    response_model=FindProductByIdResponseDto,
    summary="Get Product by ID",
    description="""
    Retrieve a product by its ID.
    
    Parameters:
    - product_id: The ID of the product to retrieve
    
    Returns:
    - The product with its details including ID, name, price, status, and availability
    - 404 Not Found if the product is not found
    """
)
async def get_product_by_id(
    product_id: str, use_case: FindProductById = Depends(find_product_by_id_use_case)
) -> FindProductByIdResponseDto:
    response = use_case(FindProductByIdRequest(product_id=product_id))
    response_dto: FindProductByIdResponseDto = FindProductByIdResponseDto(
        **response._asdict()
    )
    return response_dto


@product_router.post(
    "/",
    response_model=CreateProductResponseDto,
    status_code=status.HTTP_201_CREATED,
    summary="Create a New Product",
    description="""
    Create a new product in the catalog.
    
    Parameters:
    - product_id: The ID of the product to create
    - user_id: The ID of the user creating the product
    - name: The name of the product
    - description: The description of the product
    - price: The price of the product
    - location: The location of the product
    - status: The status of the product (New, Used, or For parts)
    - is_available: The availability status of the product (true/false)
    
    Returns:
    - The created product with its details including ID, name, price, status, and availability
    - 422 Unprocessable Entity if the request is invalid
    - 500 Internal Server Error if an unexpected error occurs
    """
)
async def create_product(
    request: CreateProductRequestDto,
    use_case: CreateProduct = Depends(create_product_use_case),
) -> CreateProductResponseDto:
    try:
        # Validate product_id is numeric
        if not request.product_id.isdigit():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[{
                    "loc": ["body", "product_id"],
                    "msg": "product_id should be numbers only",
                    "type": "value_error"
                }]
            )
        
        # Validate status
        if request.status.lower() not in [s.value.lower() for s in ProductStatuses]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[{
                    "loc": ["body", "status"],
                    "msg": f"status must be one of: {', '.join([s.value for s in ProductStatuses])}",
                    "type": "value_error.enum"
                }]
            )
        
        # Create product request
        product_request = CreateProductRequest(
            product_id=request.product_id,
            user_id=request.user_id,
            name=request.name,
            description=request.description,
            price=request.price,
            location=request.location,
            status=request.status,
            is_available=request.is_available,
        )
        
        # Call use case
        response = use_case(product_request)
        
        # Convert response to DTO
        return CreateProductResponseDto(
            product_id=response.product_id,
            user_id=response.user_id,
            name=response.name,
            description=response.description,
            price=response.price,
            location=response.location,
            status=response.status,
            is_available=response.is_available
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{
                "loc": ["body"],
                "msg": str(e),
                "type": "value_error"
            }]
        )
    except ProductRepositoryException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logging.error(f"Unexpected error in create_product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@product_router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Product",
    description="""
    Delete a product by its ID.
    
    Parameters:
    - product_id: The ID of the product to delete
    
    Returns:
    - 204 No Content if the product is deleted successfully
    - 404 Not Found if the product is not found
    - 500 Internal Server Error if an unexpected error occurs
    """
)
async def delete_product(
    product_id: str,
    use_case: DeleteProduct = Depends(delete_product_use_case)
):
    logging.info(f"Deleting product with ID {product_id}")
    try:
        # Create the request object
        request = DeleteProductRequest(product_id=product_id)
        # Call use case
        use_case(request)
        return None
    except ValueError as e:
        logging.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except ProductNotFoundException as e:
        logging.error(f"Product not found: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ProductRepositoryException as e:
        logging.error(f"Repository error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logging.error(f"Error deleting product: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@product_router.put(
    "/{product_id}",
    response_model=UpdateProductResponseDto,
    summary="Update a Product",
    description="""
    Update a product by its ID.
    
    Parameters:
    - product_id: The ID of the product to update
    - user_id: The ID of the user updating the product
    - name: The new name of the product
    - description: The new description of the product
    - price: The new price of the product
    - location: The new location of the product
    - status: The new status of the product (New, Used, or For parts)
    - is_available: The new availability status of the product (true/false)
    
    Returns:
    - The updated product with its details including ID, name, price, status, and availability
    - 404 Not Found if the product is not found
    - 500 Internal Server Error if an unexpected error occurs
    """
)
async def update_product(
    product_id: str, 
    request: UpdateProductRequestDto,
    use_case: UpdateProduct = Depends(update_product_use_case),    
) -> UpdateProductResponseDto | str:
    # Convert the DTO to the request model expected by the use case
    update_request = UpdateProductRequest(
        product_id=product_id,
        user_id=request.user_id,
        name=request.name,
        description=request.description,
        price=request.price,
        location=request.location,
        status=request.status,
        is_available=request.is_available,
    )
    
    # Call the use case
    response = use_case(product_id, update_request)
    
    if response:
        # Convert the response to updateProductResponseDto
        return UpdateProductResponseDto(
            product_id=response.product_id,
            user_id=response.user_id,
            name=response.name,
            description=response.description,
            price=response.price,
            location=response.location,
            status=response.status,
            is_available=response.is_available
        )
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")


@product_router.get(
    "/status",
    summary="Health Check",
    description="""
    Health check endpoint for AWS.
    
    Returns:
    - A JSON object with the status and timestamp
    """
)
async def get_status():
    """Health check endpoint for AWS."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}