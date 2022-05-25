from fastapi.testclient import TestClient

from pinning_service.main import app

client = TestClient(app)
