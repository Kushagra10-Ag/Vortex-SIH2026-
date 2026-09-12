from app import create_app


def make_client():
    app = create_app()
    app.config.update(TESTING=True, DEVICE_API_KEY="test-device-key")
    return app.test_client()


def test_camera_event_requires_device_key():
    client = make_client()
    response = client.post("/monitoring/camera-events", json={})
    assert response.status_code == 401


def test_camera_event_validates_payload():
    client = make_client()
    response = client.post(
        "/monitoring/camera-events",
        json={},
        headers={"X-API-Key": "test-device-key"},
    )
    assert response.status_code == 400
    assert "device_id" in response.get_json()["error"]


def test_sensor_reading_validates_payload():
    client = make_client()
    response = client.post(
        "/sensors/readings",
        json={"device_id": "edge-1"},
        headers={"X-API-Key": "test-device-key"},
    )
    assert response.status_code == 400
    assert "sensor_id" in response.get_json()["error"]


def test_device_registration_validates_payload():
    client = make_client()
    response = client.post(
        "/devices/register",
        json={},
        headers={"X-API-Key": "test-device-key"},
    )
    assert response.status_code == 400


def test_alert_creation_validates_payload():
    client = make_client()
    response = client.post(
        "/alerts",
        json={"title": "test", "message": "test", "severity": "invalid"},
        headers={"X-API-Key": "test-device-key"},
    )
    assert response.status_code == 400


def test_device_write_rate_limit():
    from app.middleware.auth import _device_rate_windows

    _device_rate_windows.clear()
    client = make_client()
    client.application.config["DEVICE_RATE_LIMIT_PER_MINUTE"] = 1
    headers = {"X-API-Key": "test-device-key"}

    assert client.post("/devices/register", json={}, headers=headers).status_code == 400
    assert client.post("/devices/register", json={}, headers=headers).status_code == 429


def test_request_body_size_limit():
    client = make_client()
    client.application.config["MAX_CONTENT_LENGTH"] = 16
    response = client.post(
        "/devices/register",
        data="x" * 32,
        content_type="application/json",
        headers={"X-API-Key": "test-device-key"},
    )
    assert response.status_code == 413