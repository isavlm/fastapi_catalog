from decimal import Decimal
from faker import Faker
from unittest.mock import MagicMock
from fastapi import status

from app.src.core.models._product import Product, ProductStatuses
from api.src.dtos.product import DeleteProductRequest
from app.src.use_cases.product.get_by_status.request import FilterProductsByStatusRequest
from factories.use_cases.product import (
    list_product_use_case,
    filter_product_use_case,
    create_product_use_case,
    delete_product_use_case
)

fake = Faker()

def test_get_products_success(test_client, mock_db_session):
    mock_response = MagicMock()
    products = [Product(
        product_id=str(fake.pyint()),  # Using numeric ID
        user_id=fake.uuid4(),
        name=fake.word(),
        description=fake.sentence(),
        price=Decimal(fake.pyint(min_value=0, max_value=9999, step=1)),
        location=fake.address(),
        status=ProductStatuses.FOR_PARTS,
        is_available=fake.boolean())]

    mock_response.products = products
    mock_use_case = MagicMock(return_value=mock_response)

    test_client.app.dependency_overrides[list_product_use_case] = lambda: mock_use_case

    response = test_client.get("/products/")

    assert response.status_code == 200

    expected_response = {
        "products": [{
            "product_id": products[0].product_id,
            "user_id": products[0].user_id,
            "name": products[0].name,
            "description": products[0].description,
            "price": str(products[0].price),
            "location": products[0].location,
            "status": "For parts",
            "is_available": products[0].is_available,
        }]}

    # Print for debugging
    print("\nActual response:", response.json())
    print("\nExpected response:", expected_response)
    print("\nProduct status:", products[0].status)
    print("\nProduct status value:", products[0].status.value)

    assert response.json() == expected_response

def test_get_products_empty_list(test_client, mock_db_session):
    mock_response = MagicMock()
    products = []

    mock_response.products = products
    mock_use_case = MagicMock(return_value=mock_response)

    test_client.app.dependency_overrides[list_product_use_case] = lambda: mock_use_case

    response = test_client.get("/products/")

    assert response.status_code == 200
    assert response.json() == {"products": []}

def test_filter_products_success(test_client, mock_db_session):
    mock_response = MagicMock()
    products = [
        Product(
            product_id=str(fake.pyint()),  # Using numeric ID
            user_id=fake.uuid4(),
            name=fake.word(),
            description=fake.sentence(),
            price=Decimal(fake.pyint(min_value=0, max_value=9999, step=1)),
            location=fake.address(),
            status=ProductStatuses.NEW,
            is_available=fake.boolean()
        )
    ]

    mock_response.products = products
    mock_use_case = MagicMock(return_value=mock_response)

    test_client.app.dependency_overrides[filter_product_use_case] = lambda: mock_use_case

    response = test_client.get("/products/filter-by-status?status_param=New")

    assert response.status_code == 200

    expected_response = {
        "products": [{
            "product_id": products[0].product_id,
            "user_id": products[0].user_id,
            "name": products[0].name,
            "description": products[0].description,
            "price": str(products[0].price),
            "location": products[0].location,
            "status": products[0].status.value,
            "is_available": products[0].is_available,
        }]}
    assert response.json() == expected_response
    # Check that the use case was called with the correct argument
    assert mock_use_case.call_count == 1
    args = mock_use_case.call_args[0]
    assert len(args) == 1
    assert args[0].status == ProductStatuses.NEW

def test_filter_products_invalid_status(test_client, mock_db_session):
    mock_response = MagicMock()
    products = []

    mock_response.products = products
    mock_use_case = MagicMock(side_effect=ValueError("Invalid status"))

    test_client.app.dependency_overrides[filter_product_use_case] = lambda: mock_use_case

    response = test_client.get("/products/filter-by-status?status_param=INVALID_STATUS")

    assert response.status_code == 422

def test_create_product_success(test_client, mock_db_session):
    product_data = {
        "product_id": str(fake.pyint()),
        "user_id": fake.uuid4(),
        "name": fake.word(),
        "description": fake.sentence(),
        "price": str(Decimal(fake.pyint(min_value=0, max_value=9999, step=1))),
        "location": fake.address(),
        "status": ProductStatuses.NEW.value,
        "is_available": fake.boolean()
    }

    mock_response = Product(**product_data)
    mock_use_case = MagicMock(return_value=mock_response)

    test_client.app.dependency_overrides[create_product_use_case] = lambda: mock_use_case

    response = test_client.post("/products/", json=product_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == product_data

def test_create_product_invalid_status(test_client, mock_db_session):
    product_data = {
        "product_id": str(fake.pyint()),
        "user_id": fake.uuid4(),
        "name": fake.word(),
        "description": fake.sentence(),
        "price": str(Decimal(fake.pyint(min_value=0, max_value=9999, step=1))),
        "location": fake.address(),
        "status": "INVALID_STATUS",
        "is_available": fake.boolean()
    }

    response = test_client.post("/products/", json=product_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_product_missing_required_field(test_client, mock_db_session):
    product_data = {
        "product_id": str(fake.pyint()),
        "name": fake.word(),
        "description": fake.sentence(),
        "price": str(Decimal(fake.pyint(min_value=0, max_value=9999, step=1))),
        "location": fake.address(),
        "status": ProductStatuses.NEW.value,
        "is_available": fake.boolean()
    }

    response = test_client.post("/products/", json=product_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_delete_product_success(test_client, mock_db_session):
    product_id = str(fake.pyint())  # Using numeric ID
    mock_use_case = MagicMock(return_value=None)

    test_client.app.dependency_overrides[delete_product_use_case] = lambda: mock_use_case

    response = test_client.delete(f"/products/{product_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    # Check that the use case was called with the correct argument
    assert mock_use_case.call_count == 1
    args = mock_use_case.call_args[0]
    assert len(args) == 1
    # Check the request object's attributes
    request = args[0]
    assert hasattr(request, 'product_id')
    assert request.product_id == product_id
