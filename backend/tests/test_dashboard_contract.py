from app import create_app
from app.controllers import dashboard_controller


def test_dashboard_overview_contract(monkeypatch):
    app = create_app()
    app.config.update(TESTING=True)
    expected = {"sales": {"total_sales": 10.0}, "devices": {"total": 1}}
    monkeypatch.setattr(dashboard_controller, "get_dashboard_overview", lambda: expected)

    response = app.test_client().get("/dashboard/overview")

    assert response.status_code == 200
    assert response.get_json() == {"success": True, "data": expected}


def test_dashboard_full_contract(monkeypatch):
    app = create_app()
    app.config.update(TESTING=True)
    expected = {"kpis": {}, "charts": {}, "devices": []}
    monkeypatch.setattr(dashboard_controller, "get_full_dashboard", lambda: expected)

    response = app.test_client().get("/dashboard/full")

    assert response.status_code == 200
    assert response.get_json() == {"success": True, "data": expected}