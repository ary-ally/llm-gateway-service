"""Response models for the public API.

TriageResponse is intentionally independent of any LLM provider so that
LLM-generated JSON can later be validated with
`TriageResponse.model_validate_json(...)`.
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TriageResponse(BaseModel):
    """Structured triage result returned by POST /triage."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "category": "database",
                    "severity": "high",
                    "likely_cause": "Database connection refused",
                    "suggested_next_step": "Verify database availability and network connectivity",
                }
            ]
        },
    )

    category: str = Field(min_length=1, max_length=64)
    severity: Severity
    likely_cause: str = Field(min_length=1, max_length=1000)
    suggested_next_step: str = Field(min_length=1, max_length=1000)