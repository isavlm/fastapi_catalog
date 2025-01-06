import pytest
from unittest.mock import MagicMock
from faker import Faker
from app.src.core.models._product import Product
from app.src.core.enums._product_statuses import ProductStatuses
from app.src.use_cases.product.get_by_status.use_case import FilterProductByStatus
from app.src.use_cases.product.get_by_status.request import FilterProductsByStatusRequest
from app.src.exceptions import ProductRepositoryException

fake = Faker()

@pytest.fixture
def mock_product_repository():
    return MagicMock()

@pytest.fixture
def fake_product_list():
    return [
        Product(
            product_id=fake.numerify(text='####'),
            user_id=fake.uuid4(),
            name=fake.word(),
            description=fake.text(),
            price=fake.pydecimal(left_digits=4, right_digits=2, positive=True),
            location=fake.address(),
            status=ProductStatuses.NEW,
            is_available=fake.boolean()
        )
    ]

def test_filter_products_success(mock_product_repository, fake_product_list):
    """Test filtering products successfully"""
    # Arrange
    filter_by = ProductStatuses.NEW
    mock_product_repository.filter.return_value = fake_product_list
    
    filter_product = FilterProductByStatus(product_repository=mock_product_repository)
    request = FilterProductsByStatusRequest(status=filter_by)
    
    # Act
    response = filter_product(request)
    
    # Assert
    mock_product_repository.filter.assert_called_once_with(filter_by)
    assert response.products == fake_product_list
    assert all(p.status == ProductStatuses.NEW for p in response.products)

def test_filter_products_repository_exception(mock_product_repository):
    """Test handling repository exception when filtering products"""
    # Arrange
    filter_by = ProductStatuses.USED
    mock_product_repository.filter.side_effect = ProductRepositoryException(method="filter")
    
    filter_product = FilterProductByStatus(product_repository=mock_product_repository)
    request = FilterProductsByStatusRequest(status=filter_by)
    
    # Act & Assert
    with pytest.raises(ProductRepositoryException) as exc_info:
        filter_product(request)
    assert str(exc_info.value) == "Exception while executing filter in Product"
    mock_product_repository.filter.assert_called_once_with(filter_by)
