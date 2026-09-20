import pytest
from pydantic import ValidationError

from app.models.responses import Severity, TriageResponse

VALID = {
    "category": "database",
    "severity": "high",
    "likely_cause": "Database connection refused",
    "suggested_next_step": "Verify database availability and network connectivity",
}


def test_valid_triage_response():
    response = TriageResponse(**VALID)
    assert response.severity is Severity.HIGH
    assert response.category == "database"


@pytest.mark.parametrize("severity", ["low", "medium", "high", "critical"])
def test_all_severity_values_accepted(severity):
    assert TriageResponse(**{**VALID, "severity": severity}).severity.value == severity


def test_invalid_severity():
    with pytest.raises(ValidationError):
        TriageResponse(**{**VALID, "severity": "unknown"})


@pytest.mark.parametrize("field", list(VALID))
def test_missing_required_response_field(field):
    data = {k: v for k, v in VALID.items() if k != field}
    with pytest.raises(ValidationError):
        TriageResponse(**data)


def test_validates_llm_style_json():
    raw = (
        '{"category": "database", "severity": "critical", '
        '"likely_cause": "x", "suggested_next_step": "y"}'
    )
    assert TriageResponse.model_validate_json(raw).severity is Severity.CRITICAL
    with pytest.raises(ValidationError):
        TriageResponse.model_validate_json(raw.replace("critical", "catastrophic"))