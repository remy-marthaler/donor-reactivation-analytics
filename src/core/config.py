
import os

# Toggle between real API and mock API (default: mock for dev)
USE_MOCK_API = os.getenv("USE_MOCK_API", "true").lower() in {"1","true","yes","y"}

# Real API base URL and token (if you switch off mock)
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.example.com")
API_TOKEN = os.getenv("API_TOKEN", "")
