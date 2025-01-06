import pytest
from unittest.mock import MagicMock
from app.src.core.models._product import Product
from faker import Faker

fake = Faker()

@pytest.fixture
def mock_product_repository():
    """Mock product repository for tests"""
    repository = MagicMock()
    repository.get_by_id.return_value = None
    repository.create.return_value = Product(
        product_id=str(fake.pyint(min_value=1000, max_value=9999)),
        user_id=fake.uuid4(),
        name=fake.word(),
        description=fake.sentence(),
        price=fake.pydecimal(min_value=0, max_value=9999, right_digits=2),
        location=fake.address(),
        status="New",
        is_available=fake.boolean()
    )
    repository.filter_by_status.return_value = []
    return repository

@pytest.fixture
def fake_product_list():
    """Generate a list of fake products for testing"""
    return [
        Product(
            product_id=str(fake.pyint(min_value=1000, max_value=9999)),
            user_id=fake.uuid4(),
            name=fake.word(),
            description=fake.sentence(),
            price=fake.pydecimal(min_value=0, max_value=9999, right_digits=2),
            location=fake.address(),
            status="New",
            is_available=fake.boolean()
        )
        for _ in range(2)
    ]
