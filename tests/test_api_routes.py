from apps.api.app.api import router
from apps.api.app.main import app


def test_api_exposes_phase1_routes():
    app_paths = {route.path for route in app.routes if hasattr(route, "path")}
    api_paths = {route.path for route in router.routes if hasattr(route, "path")}
    assert "/health" in app_paths
    assert "/ready" in app_paths
    assert "/api/v1/projects" in {"/api/v1" + path for path in api_paths}
    assert "/api/v1/approvals" in {"/api/v1" + path for path in api_paths}
    assert "/api/v1/intelligence/runs" in {"/api/v1" + path for path in api_paths}
