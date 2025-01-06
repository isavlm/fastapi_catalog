import pytest
from fastapi.testclient import TestClient
from app.src.core import ProductStatuses
from fastapi import status
from decimal import Decimal

# Test data
test_product = {
    "product_id": "1234",
    "user_id": "IVLM",
    "name": "Test Product",
    "description": "Test Description",
    "price": "100.00",
    "location": "Test Location",
    "status": ProductStatuses.NEW.value,
    "is_available": True
}

def test_get_products_empty_list(test_client: TestClient):
    """Test getting products when the database is empty"""
    response = test_client.get("/products/")
    assert response.status_code == 200
    assert response.json() == {"products": []}

def test_get_products_with_data(test_client: TestClient, create_test_product):
    """Test getting products when there is data in the database"""
    # Create a test product with unique product_id
    test_product_data = {
        "product_id": "1234",
        "user_id": "IVLM",
        "name": "Test Product",
        "description": "Test Description",
        "price": "100.00",
        "location": "Test Location",
        "status": ProductStatuses.NEW.value,
        "is_available": True
    }
    
    # Create a test product
    response = test_client.post("/products/", json=test_product_data)
    assert response.status_code == status.HTTP_201_CREATED

    # Get all products
    response = test_client.get("/products/")
    assert response.status_code == 200
    products = response.json()["products"]
    assert len(products) == 1
    assert products[0]["product_id"] == test_product_data["product_id"]

def test_filter_products_success(test_client, fake_product_list):
    """Test filtering products successfully"""
    # Arrange
    test_product = {
        "product_id": "1234",
        "user_id": "IVLM",
        "name": "Test Product",
        "description": "Test Description",
        "price": "100.00",
        "location": "Test Location",
        "status": ProductStatuses.NEW.value,
        "is_available": True
    }
    
    # Create a test product with known status
    response = test_client.post("/products/", json=test_product)
    assert response.status_code == status.HTTP_201_CREATED
    
    # Act
    response = test_client.get(f"/products/filter-by-status?status_param={test_product['status']}")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    filtered_products = response.json()["products"]
    assert len(filtered_products) > 0
    assert all(p["status"].lower() == test_product["status"].lower() for p in filtered_products)

def test_filter_products_invalid_status(test_client):
    """Test filtering products with invalid status"""
    # Arrange
    invalid_status = "invalid_status"
    
    # Act
    response = test_client.get(f"/products/filter-by-status?status={invalid_status}")
    
    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data

#TESTING TO CREATE A PRODUCT. 
def test_create_product_success(test_client): # this one should pass
    """Test creating a product with valid data"""
    # Arrange
    new_product = {
        "product_id": "1234",
        "user_id": "user123",
        "name": "Test Product",
        "description": "A test product",
        "price": "99.99",
        "location": "Test Location",
        "status": "New",
        "is_available": True
    }
    
    # Act
    response = test_client.post("/products/", json=new_product)
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    created_product = response.json()
    assert created_product["product_id"] == new_product["product_id"]
    assert created_product["name"] == new_product["name"]
    assert Decimal(created_product["price"]) == Decimal(new_product["price"])

def test_create_product_invalid_id(test_client):
    """Test creating a product with invalid product_id (non-numeric)"""
    # Arrange
    invalid_product = {
        "product_id": "abc123",  # Invalid: contains letters - We dont want this.
        "user_id": "user123",
        "name": "Test Product",
        "description": "A test product",
        "price": "99.99",
        "location": "Test Location",
        "status": "New",
        "is_available": True
    }

    # Act
    response = test_client.post("/products/", json=invalid_product)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    error_detail = response.json()["detail"]
    assert any(
        error["msg"] == "Value error, product_id should be numbers only" and
        error["loc"] == ["body", "product_id"]
        for error in error_detail
    )

def test_create_product_invalid_status(test_client): # this one should fail 
    """Test creating a product with invalid status"""
    # Arrange
    invalid_product = {
        "product_id": "1234",
        "user_id": "user123",
        "name": "Test Product",
        "description": "A test product",
        "price": "99.99",
        "location": "Test Location",
        "status": "Invalid Status",  # Invalid status
        "is_available": True
    }
    
    # Act
    response = test_client.post("/products/", json=invalid_product)
    
    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    error_detail = response.json()["detail"]
    assert any("status must be one of" in error["msg"] 
              for error in error_detail)

def test_create_product_missing_required_field(test_client):
    """Test creating a product with missing required field"""
    # Arrange
    incomplete_product = {
        "product_id": "1234",
        # missing user_id
        "name": "Test Product",
        "description": "A test product",
        "price": "99.99",
        "location": "Test Location",
        "status": "New",
        "is_available": True
    }

    # Act
    response = test_client.post("/products/", json=incomplete_product)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    error_detail = response.json()["detail"]
    assert any(
        error["msg"] == "Field required" and
        error["loc"] == ["body", "user_id"]
        for error in error_detail
    )
