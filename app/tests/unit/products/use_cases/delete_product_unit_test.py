import pytest
from decimal import Decimal
from unittest.mock import MagicMock
from faker import Faker
from fastapi import HTTPException
from app.src.core.models._product import Product
from app.src.core.enums._product_statuses import ProductStatuses
from app.src.use_cases.product.delete.use_case import DeleteProduct
from app.src.use_cases.product.delete.request import DeleteProductRequest
from app.src.exceptions import ProductRepositoryException, ProductNotFoundException

fake = Faker()

@pytest.fixture
def mock_product_repository():
    return MagicMock()

@pytest.fixture
def sample_product():
    return Product(
        product_id=fake.numerify(text='####'),
        user_id=fake.uuid4(),
        name=fake.word(),
        description=fake.text(),
        price=Decimal('99.99'),
        location=fake.address(),
        status=ProductStatuses.NEW,
        is_available=True
    )

def test_delete_product_success(mock_product_repository, sample_product):
    """Test deleting a product successfully"""
    # Arrange
    mock_product_repository.get_by_id.return_value = sample_product
    mock_product_repository.delete.return_value = sample_product
    delete_product = DeleteProduct(product_repository=mock_product_repository)
    request = DeleteProductRequest(product_id=sample_product.product_id)
    
    # Act
    response = delete_product(request)
    
    # Assert
    assert response == sample_product
    mock_product_repository.delete.assert_called_once_with(sample_product.product_id)

def test_delete_product_not_found(mock_product_repository):
    """Test deleting a non-existent product"""
    # Arrange
    mock_product_repository.get_by_id.return_value = None
    delete_product = DeleteProduct(product_repository=mock_product_repository)
    request = DeleteProductRequest(product_id="nonexistent")
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        delete_product(request)
    assert exc_info.value.status_code == 404
    assert "not found" in str(exc_info.value.detail)

def test_delete_product_repository_exception(mock_product_repository, sample_product):
    """Test handling repository exception when deleting a product"""
    # Arrange
    mock_product_repository.get_by_id.return_value = sample_product
    mock_product_repository.delete.side_effect = ProductRepositoryException(method="delete")
    delete_product = DeleteProduct(product_repository=mock_product_repository)
    request = DeleteProductRequest(product_id="123")
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        delete_product(request)
    assert exc_info.value.status_code == 500
    assert "Exception while executing delete in Product" in str(exc_info.value.detail)
