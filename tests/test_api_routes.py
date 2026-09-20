from apps.api.app.main import app


def test_api_exposes_phase1_routes():
    paths = {route.path for route in app.routes}
    assert "/health" in paths
    assert "/ready" in paths
    assert "/api/v1/projects" in paths
    assert "/api/v1/approvals" in paths
