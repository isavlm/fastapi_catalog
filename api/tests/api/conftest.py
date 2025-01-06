import pytest
from fastapi.testclient import TestClient
from decimal import Decimal
from faker import Faker
from unittest.mock import MagicMock
from uuid import UUID

from api.src.create_app import create_app
from adapters.src.repositories.sql.session_manager import SessionManager
from adapters.src.repositories.sql.tables.product import ProductSchema
from app.src.core.models._product import Product
from app.src.core.enums._product_statuses import ProductStatuses
from app.src.exceptions import ProductRepositoryException

fake = Faker()

@pytest.fixture(autouse=True)
def mock_db_session():
    """Mock database session for all tests"""
    session_mock = MagicMock()
    
    # Make session work as a context manager
    session_mock.__enter__.return_value = session_mock
    session_mock.__exit__.return_value = None
    
    # Initialize in-memory product storage
    session_mock.products = []
    
    # Create query mock with proper chaining
    query_mock = MagicMock()
    session_mock.query.return_value = query_mock
    
    def mock_filter(condition):
        """Mock filter operations for different queries"""
        try:
            # For status filtering
            if hasattr(condition.right, 'value') and hasattr(condition.left, 'key') and condition.left.key == 'status':
                status = condition.right.value
                filtered_products = [p for p in session_mock.products if p.status.lower() == status.lower()]
                query_mock.all.return_value = filtered_products
                return query_mock
            
            # For product_id filtering
            if hasattr(condition.left, 'key') and condition.left.key == 'product_id':
                product_id = condition.right
                product = next((p for p in session_mock.products if p.product_id == product_id), None)
                query_mock.first.return_value = product
                return query_mock
                
            # Default case - return all products
            query_mock.first.return_value = None
            query_mock.all.return_value = session_mock.products
            return query_mock
        except Exception as e:
            print(f"Error in mock_filter: {str(e)}")
            raise
    
    # Set up mock behaviors
    query_mock.filter.side_effect = mock_filter
    query_mock.all.return_value = session_mock.products
    
    def mock_add(product):
        """Add product to in-memory storage"""
        try:
            if isinstance(product, ProductSchema):
                # Check if product already exists
                existing = next((p for p in session_mock.products if p.product_id == product.product_id), None)
                if not existing:
                    session_mock.products.append(product)
            else:
                # Convert Product model to ProductSchema
                schema = ProductSchema(
                    product_id=product.product_id,
                    user_id=product.user_id,
                    name=product.name,
                    description=product.description,
                    price=product.price,
                    location=product.location,
                    status=product.status,
                    is_available=product.is_available
                )
                # Check if product already exists
                existing = next((p for p in session_mock.products if p.product_id == schema.product_id), None)
                if not existing:
                    session_mock.products.append(schema)
        except Exception as e:
            print(f"Error in mock_add: {str(e)}")
            raise ProductRepositoryException(method="create", message=str(e))
    
    def mock_commit():
        """Mock commit operation"""
        pass
    
    # Attach mock methods
    session_mock.add = mock_add
    session_mock.commit = mock_commit
    
    # Set up the session
    SessionManager._session = session_mock
    yield session_mock
    # Clean up after test
    SessionManager._session = None
    session_mock.products = []

@pytest.fixture
def test_client() -> TestClient:
    api = create_app()
    client = TestClient(api)
    return client

@pytest.fixture
def api_client(test_client):
    """Alias for test_client to maintain compatibility"""
    return test_client

@pytest.fixture
def mock_product_repository():
    """Mock product repository for tests"""
    repository = MagicMock()
    repository.get_by_id.return_value = None
    repository.create.return_value = fake_product()
    repository.filter_by_status.return_value = []
    return repository

@pytest.fixture
def fake_product_list():
    return [Product(
        product_id=str(fake.pyint(min_value=1000, max_value=9999)),  # 4-digit number as string
        user_id=fake.uuid4(),  # This can stay as UUID
        name=fake.word(),
        description=fake.sentence(),
        price=Decimal(fake.pyint(min_value=0, max_value=9999, step=1)),
        location=fake.address(),
        status=fake.random_element(elements=(
            ProductStatuses.NEW, ProductStatuses.USED, ProductStatuses.FOR_PARTS)),
        is_available=fake.boolean()
    ) for _ in range(2)]

@pytest.fixture
def fake_database_product_list():
    return [ProductSchema(
        product_id=str(fake.pyint(min_value=1000, max_value=9999)),  # 4-digit number as string
        user_id=fake.uuid4(),  # This can stay as UUID
        name=fake.word(),
        description=fake.sentence(),
        price=Decimal(fake.pyint(min_value=0, max_value=9999, step=1)),
        location=fake.address(),
        status=fake.random_element(elements=("New", "Used", "For parts")),
        is_available=fake.boolean()
    ) for _ in range(2)]

@pytest.fixture
def fake_product():
    return Product(
        product_id=str(fake.pyint(min_value=1000, max_value=9999)),  # 4-digit number as string
        user_id=fake.uuid4(),  # This can stay as UUID
        name=fake.word(),
        description=fake.sentence(),
        price=Decimal(fake.pyint(min_value=0, max_value=9999, step=1)),
        location=fake.address(),
        status=fake.random_element(elements=(
            ProductStatuses.NEW, ProductStatuses.USED, ProductStatuses.FOR_PARTS)),
        is_available=fake.boolean()
    )

@pytest.fixture
def create_test_product(test_client, fake_product):
    """Helper fixture to create a test product"""
    def _create_product(product_data=None):
        if product_data is None:
            product_data = {
                "product_id": fake_product.product_id,
                "user_id": str(fake_product.user_id),
                "name": fake_product.name,
                "description": fake_product.description,
                "price": str(fake_product.price),
                "location": fake_product.location,
                "status": fake_product.status.value,
                "is_available": fake_product.is_available
            }
        
        # Create product through API
        response = test_client.post("/products/", json=product_data)
        
        # If creation successful, convert to ProductSchema and add to mock database
        if response.status_code == 201:
            schema = ProductSchema(
                product_id=product_data["product_id"],
                user_id=product_data["user_id"],
                name=product_data["name"],
                description=product_data["description"],
                price=Decimal(product_data["price"]),
                location=product_data["location"],
                status=product_data["status"],
                is_available=product_data["is_available"]
            )
            SessionManager._session.products.append(schema)
            
        return response, product_data
    return _create_product
