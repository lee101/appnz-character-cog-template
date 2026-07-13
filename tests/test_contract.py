from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_health_and_schema() -> None:
    assert client.get("/health-check").json() == {"status": "READY"}
    schema = client.get("/openapi.json").json()
    assert schema["outputKind"] == "json"
    assert {item["name"] for item in schema["inputs"]} >= {"portrait", "audio", "driving_video"}


def test_prediction_contract() -> None:
    response = client.post(
        "/predictions",
        json={"input": {"portrait": "https://example.test/face.png", "audio": "https://example.test/voice.wav"}},
    )
    body = response.json()
    assert body["status"] == "succeeded"
    assert body["output"]["driver_kind"] == "audio"
    assert body["output"]["timing_ms"] >= 0


def test_bounded_validation_error() -> None:
    body = client.post("/predictions", json={"input": {"portrait": "file:///etc/passwd"}}).json()
    assert body["status"] == "failed"
    assert "portrait" in body["error"]
