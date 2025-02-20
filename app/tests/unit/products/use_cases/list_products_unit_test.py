import pytest
from decimal import Decimal
from unittest.mock import MagicMock
from faker import Faker
from app.src.core.models._product import Product
from app.src.core.enums._product_statuses import ProductStatuses
from app.src.use_cases.product.list_all.use_case import ListProducts
from app.src.exceptions import ProductRepositoryException

fake = Faker()

@pytest.fixture
def mock_product_repository():
    return MagicMock()

@pytest.fixture
def sample_products():
    return [
        Product(
            product_id=fake.numerify(text='####'),
            user_id=fake.uuid4(),
            name=fake.word(),
            description=fake.text(),
            price=Decimal('99.99'),
            location=fake.address(),
            status=ProductStatuses.NEW,
            is_available=True
        ),
        Product(
            product_id=fake.numerify(text='####'),
            user_id=fake.uuid4(),
            name=fake.word(),
            description=fake.text(),
            price=Decimal('149.99'),
            location=fake.address(),
            status=ProductStatuses.USED,
            is_available=True
        )
    ]

def test_list_products_success(mock_product_repository, sample_products):
    """Test listing products successfully"""
    # Arrange
    mock_product_repository.list_all.return_value = sample_products
    list_products = ListProducts(product_repository=mock_product_repository)
    
    # Act
    response = list_products()
    
    # Assert
    assert len(response.products) == 2
    assert response.products[0].status == ProductStatuses.NEW
    assert response.products[1].status == ProductStatuses.USED
    mock_product_repository.list_all.assert_called_once()

def test_list_products_empty(mock_product_repository):
    """Test listing products when there are no products"""
    # Arrange
    mock_product_repository.list_all.return_value = []
    list_products = ListProducts(product_repository=mock_product_repository)
    
    # Act
    response = list_products()
    
    # Assert
    assert len(response.products) == 0
    mock_product_repository.list_all.assert_called_once()

def test_list_products_repository_exception(mock_product_repository):
    """Test handling repository exception when listing products"""
    # Arrange
    mock_product_repository.list_all.side_effect = ProductRepositoryException(method="list")
    list_products = ListProducts(product_repository=mock_product_repository)
    
    # Act & Assert
    with pytest.raises(ProductRepositoryException) as exc_info:
        list_products()
    assert "list" in str(exc_info.value)
