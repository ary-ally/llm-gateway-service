"""HTTP routes. This layer must stay free of any LLM provider imports."""

from fastapi import APIRouter

from app.models.requests import TriageRequest
from app.models.responses import Severity, TriageResponse

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def _mock_triage_response() -> TriageResponse:
    """Deterministic placeholder until the real triage service exists.

    Constructing a TriageResponse means the mock is validated by the same
    model that will validate real LLM output later.
    """
    return TriageResponse(
        category="database",
        severity=Severity.HIGH,
        likely_cause="Database connection refused",
        suggested_next_step="Verify database availability and network connectivity",
    )


@router.post("/triage", response_model=TriageResponse)
async def triage(payload: TriageRequest) -> TriageResponse:
    # `payload` is already validated by FastAPI/Pydantic (422 on failure).
    # The raw log is deliberately not logged or stored.
    return _mock_triage_response()