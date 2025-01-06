import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.exceptions import HTTPException
from app.src.use_cases.product import (
    ListProducts,
    ListProductResponse,
    FindProductById,
    FindProductByIdResponse,
    FindProductByIdRequest,
    CreateProduct,
    CreateProductResponse,
    CreateProductRequest,
    DeleteProductRequest,
    DeleteProductResponse,
    DeleteProduct,
    UpdateProductRequest,
    UpdateProductResponse,
    UpdateProduct,
    FilterProductByStatus,
    FilterProductsByStatusRequest,
    FilterProductsByStatusResponse
)
from app.src.core.enums._product_statuses import ProductStatuses
from app.src.exceptions import ProductNotFoundException, ProductRepositoryException
from factories.use_cases.product import get_product_repository
from ..dtos import (
    ProductBase,
    ListProductResponseDto,
    CreateProductRequestDto,
    CreateProductResponseDto,
    FindProductByIdResponseDto,
    DeleteProductResponse,
    UpdateProductRequestDto,
    UpdateProductResponseDto,
    FilterProductByStatusResponseDto,
    FilterProductsByStatusRequestDto
)
from factories.use_cases import (
    list_product_use_case,
    find_product_by_id_use_case,
    create_product_use_case,
    delete_product_use_case,
    update_product_use_case,
    filter_product_use_case
)

product_router = APIRouter(prefix="/products")


@product_router.get("/", response_model=ListProductResponseDto)
async def get_products(
    use_case: ListProducts = Depends(list_product_use_case),
) -> ListProductResponse:
    response_list = use_case()
    response = [
        {**product._asdict(), "status": str(product.status.value)}
        for product in response_list.products
    ]
    response_dto: ListProductResponseDto = ListProductResponseDto(
        products=[ProductBase(**product) for product in response]
    )
    return response_dto


#Route to filter by status
@product_router.get("/filter-by-status", response_model=FilterProductByStatusResponseDto)
async def filter_product_by_status(
    status_param: str,
    use_case: FilterProductByStatus = Depends(filter_product_use_case)
) -> FilterProductByStatusResponseDto:
    try:
        # Validate status before calling use case
        if status_param.lower() not in [s.value.lower() for s in ProductStatuses]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[{
                    "loc": ["query", "status"],
                    "msg": f"Not a valid status value. Must be one of: {', '.join([s.value for s in ProductStatuses])}",
                    "type": "value_error.enum"
                }]
            )
        
        # Create the request with the status
        response = use_case(FilterProductsByStatusRequest(status=status_param))
        
        # Convert the response to FilterProductByStatusResponseDto
        return FilterProductByStatusResponseDto(
            products=[
                ProductBase(
                    product_id=product.product_id,
                    user_id=product.user_id,
                    name=product.name,
                    description=product.description,
                    price=product.price,
                    location=product.location,
                    status=product.status,
                    is_available=product.is_available
                )
                for product in response.products
            ]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{
                "loc": ["query", "status"],
                "msg": str(e),
                "type": "value_error"
            }]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@product_router.get("/{product_id}", response_model=FindProductByIdResponseDto)
async def get_product_by_id(
    product_id: str, use_case: FindProductById = Depends(find_product_by_id_use_case)
) -> FindProductByIdResponse:
    response = use_case(FindProductByIdRequest(product_id=product_id))
    response_dto: FindProductByIdResponseDto = FindProductByIdResponseDto(
        **response._asdict()
    )
    return response_dto


@product_router.post("/", response_model=CreateProductResponseDto, status_code=status.HTTP_201_CREATED)
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


# Isadora's code starts here.

#ROUTE TO DELETE
@product_router.delete("/{product_id}", response_model=DeleteProductResponse)
async def delete_product(
    product_id: str,
    use_case: DeleteProduct = Depends(delete_product_use_case)
) -> DeleteProductResponse:
    logging.info(f"Deleting product with ID {product_id}")
    try:
        response = use_case(DeleteProductRequest(product_id=product_id))
        logging.info(f"Product deleted: {response}")
        return response
    except ProductNotFoundException as e:
        logging.error(f"Product not found: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ProductRepositoryException as e:
        logging.error(f"Repository error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logging.error(f"Error deleting product: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    


#Route to Update

@product_router.put("/{product_id}", response_model=UpdateProductResponseDto)
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