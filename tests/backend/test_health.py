import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
