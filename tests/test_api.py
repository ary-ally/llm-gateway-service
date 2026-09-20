import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.requests import MAX_LOG_LENGTH
from app.models.responses import TriageResponse

client = TestClient(app)

VALID_PAYLOAD = {
    "log": "Database connection timeout after 30 seconds",
    "metadata": {"service": "payments", "environment": "production"},
}


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_triage_success():
    response = client.post("/triage", json=VALID_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "category": "database",
        "severity": "high",
        "likely_cause": "Database connection pool exhaustion",
        "suggested_next_step": "Inspect active connections and pool utilization",
    }
    TriageResponse.model_validate(body)


def test_triage_without_metadata():
    assert client.post("/triage", json={"log": "ERROR x"}).status_code == 200


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"log": ""},
        {"log": "     "},
        {"log": "a" * (MAX_LOG_LENGTH + 1)},
        {"log": "x", "metadata": {"service": 123}},
        {"log": "x", "metadata": "not-a-dict"},
        {"log": 123},
    ],
    ids=[
        "missing-log",
        "empty-log",
        "whitespace-log",
        "oversized-log",
        "metadata-non-string-value",
        "metadata-not-a-dict",
        "log-not-a-string",
    ],
)
def test_triage_invalid_request(payload):
    response = client.post("/triage", json=payload)
    assert response.status_code == 422