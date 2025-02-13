import pytest
from decimal import Decimal
from unittest.mock import MagicMock
from faker import Faker
from app.src.core.models._product import Product
from app.src.core.enums._product_statuses import ProductStatuses
from app.src.use_cases.product.create.use_case import CreateProduct
from app.src.use_cases.product.create.request import CreateProductRequest
from app.src.exceptions import ProductRepositoryException, ProductBusinessException

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

def test_create_product_success(mock_product_repository, sample_product):
    """Test creating a product successfully"""
    # Arrange
    mock_product_repository.get_by_id.return_value = None
    mock_product_repository.create.return_value = sample_product
    create_product = CreateProduct(product_repository=mock_product_repository)
    request = CreateProductRequest(
        product_id=sample_product.product_id,
        user_id=sample_product.user_id,
        name=sample_product.name,
        description=sample_product.description,
        price=sample_product.price,
        location=sample_product.location,
        status=sample_product.status,
        is_available=sample_product.is_available
    )
    
    # Act
    response = create_product(request)
    
    # Assert
    assert response.product_id == sample_product.product_id
    assert response.user_id == sample_product.user_id
    assert response.name == sample_product.name
    mock_product_repository.create.assert_called_once()

def test_create_product_repository_exception(mock_product_repository):
    """Test handling repository exception when creating a product"""
    # Arrange
    mock_product_repository.get_by_id.return_value = None
    mock_product_repository.create.side_effect = ProductRepositoryException(method="create")
    create_product = CreateProduct(product_repository=mock_product_repository)
    request = CreateProductRequest(
        product_id=fake.numerify(text='####'),
        user_id=fake.uuid4(),
        name=fake.word(),
        description=fake.text(),
        price=Decimal('99.99'),
        location=fake.address(),
        status=ProductStatuses.NEW,
        is_available=True
    )
    
    # Act & Assert
    with pytest.raises(ProductBusinessException) as exc_info:
        create_product(request)
    assert "create" in str(exc_info.value)
