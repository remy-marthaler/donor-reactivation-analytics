
from .config import USE_MOCK_API
from ..data_access.api_client import ApiClient
from ..data_access.mock_api_client import MockApiClient

def get_api_client():
    """Return the configured API client (mock or real)."""
    if USE_MOCK_API:
        return MockApiClient()
    return ApiClient()
