import pytest
from pydantic import ValidationError

from app.models.requests import (
    MAX_LOG_LENGTH,
    MAX_METADATA_ITEMS,
    MAX_METADATA_KEY_LENGTH,
    MAX_METADATA_VALUE_LENGTH,
    TriageRequest,
)


def test_valid_triage_request():
    log = "ERROR database connection refused"
    request = TriageRequest(
        log=log,
        metadata={"service": "payment-service", "environment": "production"},
    )
    assert request.log == log  # input is never modified or truncated
    assert request.metadata == {"service": "payment-service", "environment": "production"}


def test_missing_log():
    with pytest.raises(ValidationError):
        TriageRequest()


def test_empty_log():
    with pytest.raises(ValidationError):
        TriageRequest(log="")


@pytest.mark.parametrize("value", ["     ", "\n\t  \n"])
def test_whitespace_only_log(value):
    with pytest.raises(ValidationError):
        TriageRequest(log=value)


def test_log_size_limit():
    assert TriageRequest(log="a" * MAX_LOG_LENGTH).log == "a" * MAX_LOG_LENGTH
    with pytest.raises(ValidationError):
        TriageRequest(log="a" * (MAX_LOG_LENGTH + 1))


def test_valid_metadata():
    assert TriageRequest(log="x").metadata is None
    assert TriageRequest(log="x", metadata={}).metadata == {}
    assert TriageRequest(log="x", metadata={"service": "api"}).metadata == {"service": "api"}

def test_metadata_omitted():
    request = TriageRequest(log="Database connection timeout after 30 seconds")
    assert request.metadata is None

@pytest.mark.parametrize(
    "metadata",
    [
        "not-a-dict",
        ["service", "api"],
        {"service": 123},
        {"service": None},
        {123: "value"},
        {"": "value"},
        {"k" * (MAX_METADATA_KEY_LENGTH + 1): "value"},
        {"key": "v" * (MAX_METADATA_VALUE_LENGTH + 1)},
        {f"key{i}": "v" for i in range(MAX_METADATA_ITEMS + 1)},
    ],
)
def test_invalid_metadata(metadata):
    with pytest.raises(ValidationError):
        TriageRequest(log="x", metadata=metadata)