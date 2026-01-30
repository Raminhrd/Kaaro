import pytest
from django.test import override_settings
from rest_framework.test import APIClient

TEST_CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-cache",
    }
}

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture(autouse=True)
def _use_test_cache():
    with override_settings(CACHES=TEST_CACHES):
        yield
