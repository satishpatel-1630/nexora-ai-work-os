from fastapi.testclient import TestClient
from apps.api.app.main import app
def test_health():
    r=TestClient(app).get("/health")
    assert r.status_code==200 and r.json()["status"]=="ok"
    assert r.headers["x-request-id"]
