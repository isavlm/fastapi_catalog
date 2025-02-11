import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.src.core.models._product import Product
from app.src.core.enums._product_statuses import ProductStatuses
from app.src.exceptions import ProductRepositoryException
from adapters.src.repositories.sql.sql_product_repository import SQLProductRepository
from adapters.src.repositories.sql.tables.product import ProductSchema

@pytest.fixture
def mock_session():
    session = MagicMock(spec=Session)
    # Mock the context manager
    session.__enter__.return_value = session
    session.__exit__.return_value = None
    return session

@pytest.fixture
def sample_product():
    return Product(
        product_id="123",
        user_id="user123",
        name="Test Product",
        description="Test Description",
        price=Decimal("99.99"),
        location="Test Location",
        status=ProductStatuses.NEW,
        is_available=True
    )

@pytest.fixture
def sample_product_schema():
    return ProductSchema(
        product_id="123",
        user_id="user123",
        name="Test Product",
        description="Test Description",
        price=Decimal("99.99"),
        location="Test Location",
        status=ProductStatuses.NEW,
        is_available=True
    )

def test_list_all_success(mock_session, sample_product_schema):
    # Arrange
    repository = SQLProductRepository(mock_session)
    mock_session.query.return_value.all.return_value = [sample_product_schema]
    
    # Act
    result = repository.list_all()
    
    # Assert
    assert len(result) == 1
    assert result[0].product_id == "123"
    assert result[0].name == "Test Product"
    mock_session.query.assert_called_once_with(ProductSchema)

def test_list_all_empty(mock_session):
    # Arrange
    repository = SQLProductRepository(mock_session)
    mock_session.query.return_value.all.return_value = []
    
    # Act
    result = repository.list_all()
    
    # Assert
    assert len(result) == 0
    mock_session.query.assert_called_once_with(ProductSchema)

def test_list_all_exception(mock_session):
    # Arrange
    repository = SQLProductRepository(mock_session)
    mock_session.query.side_effect = Exception("Database error")
    
    # Act & Assert
    with pytest.raises(ProductRepositoryException) as exc_info:
        repository.list_all()
    assert str(exc_info.value) == "Exception while executing list in Product"

def test_create_success(mock_session, sample_product):
    # Arrange
    repository = SQLProductRepository(mock_session)
    
    # Act
    with patch('adapters.src.repositories.sql.sql_product_repository.ProductSchema') as mock_schema:
        result = repository.create(sample_product)
        
        # Assert
        assert result == sample_product
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

def test_create_exception(mock_session, sample_product):
    # Arrange
    repository = SQLProductRepository(mock_session)
    mock_session.add.side_effect = Exception("Database error")
    
    # Act & Assert
    with pytest.raises(ProductRepositoryException) as exc_info:
        repository.create(sample_product)
    assert str(exc_info.value) == "Exception while executing create in Product"

def test_get_by_id_success(mock_session, sample_product_schema):
    # Arrange
    repository = SQLProductRepository(mock_session)
    mock_session.query.return_value.filter.return_value.first.return_value = sample_product_schema
    
    # Act
    result = repository.get_by_id("123")
    
    # Assert
    assert result.product_id == "123"
    assert result.name == "Test Product"
    mock_session.query.assert_called_once_with(ProductSchema)

def test_get_by_id_not_found(mock_session):
    # Arrange
    repository = SQLProductRepository(mock_session)
    mock_session.query.return_value.filter.return_value.first.return_value = None
    
    # Act
    result = repository.get_by_id("123")
    
    # Assert
    assert result is None

def test_delete_success(mock_session, sample_product_schema):
    # Arrange
    repository = SQLProductRepository(mock_session)
    mock_session.query.return_value.filter.return_value.first.return_value = sample_product_schema
    
    # Act
    result = repository.delete("123")
    
    # Assert
    assert result.product_id == "123"
    assert result.name == "Test Product"
    mock_session.commit.assert_called_once()

def test_delete_not_found(mock_session):
    # Arrange
    repository = SQLProductRepository(mock_session)
    mock_session.query.return_value.filter.return_value.first.return_value = None
    
    # Act & Assert
    with pytest.raises(ProductRepositoryException) as exc_info:
        repository.delete("123")
    assert "delete" in str(exc_info.value)

def test_filter_success(mock_session, sample_product_schema):
    # Arrange
    repository = SQLProductRepository(mock_session)
    mock_session.query.return_value.filter.return_value.all.return_value = [sample_product_schema]
    
    # Act
    result = repository.filter(ProductStatuses.NEW)
    
    # Assert
    assert len(result) == 1
    assert result[0].product_id == "123"
    assert result[0].status == ProductStatuses.NEW
    mock_session.query.assert_called_once_with(ProductSchema)
