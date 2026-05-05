import pytest
from django.core.cache import cache
from django.contrib.auth import get_user_model
from feature_flag_infra.django.providers import DjangoDBFlagProvider

User = get_user_model()

@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()

@pytest.fixture
def provider():
    return DjangoDBFlagProvider(cache_ttl=30)

@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="normal_user",
        email="normal@example.com",
        password="strong-test-password",
    )

@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="staff_user",
        email="staff@example.com",
        password="strong-test-password",
        is_staff=True,
    )