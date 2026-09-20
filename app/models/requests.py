"""Request models for the public API."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Maximum accepted length of the `log` field, in characters.
# ~10k characters is roughly 2.5-3.5k tokens: enough for a stack trace or a
# focused log excerpt, while keeping future LLM prompt size, cost and latency
# bounded. Oversized input is rejected (422), never silently truncated.
MAX_LOG_LENGTH = 10_000

# Metadata is meant for a few short tags (service, environment, region, ...).
MAX_METADATA_ITEMS = 10
MAX_METADATA_KEY_LENGTH = 64
MAX_METADATA_VALUE_LENGTH = 256


class TriageRequest(BaseModel):
    """Payload accepted by POST /triage."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "log": "ERROR database connection refused",
                    "metadata": {
                        "service": "payment-service",
                        "environment": "production",
                    },
                }
            ]
        },
    )

    log: str = Field(
        min_length=1,
        max_length=MAX_LOG_LENGTH,
        description=f"Raw log text to triage (1-{MAX_LOG_LENGTH} characters).",
    )
    metadata: dict[str, str] | None = Field(
        default=None,
        description=(
            f"Optional string tags. At most {MAX_METADATA_ITEMS} entries; keys up to "
            f"{MAX_METADATA_KEY_LENGTH} chars, values up to {MAX_METADATA_VALUE_LENGTH} chars."
        ),
    )

    @field_validator("log")
    @classmethod
    def log_must_not_be_blank(cls, value: str) -> str:
        # Reject whitespace-only input. The value itself is returned unchanged.
        if not value.strip():
            raise ValueError("log must not be blank")
        return value

    @field_validator("metadata")
    @classmethod
    def metadata_must_be_bounded(
        cls, value: dict[str, str] | None
    ) -> dict[str, str] | None:
        if value is None:
            return value

        if len(value) > MAX_METADATA_ITEMS:
            raise ValueError(f"metadata may contain at most {MAX_METADATA_ITEMS} entries")

        for key, item in value.items():
            if not key.strip():
                raise ValueError("metadata keys must not be blank")
            if len(key) > MAX_METADATA_KEY_LENGTH:
                raise ValueError(
                    f"metadata keys must be at most {MAX_METADATA_KEY_LENGTH} characters"
                )
            if len(item) > MAX_METADATA_VALUE_LENGTH:
                raise ValueError(
                    f"metadata values must be at most {MAX_METADATA_VALUE_LENGTH} characters"
                )
        return value