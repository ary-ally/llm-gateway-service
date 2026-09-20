# Aegis Core — LLM Gateway Service

A FastAPI service that will triage infrastructure logs using LLM providers
behind a provider abstraction (Anthropic and OpenAI, with retries, fallback,
structured output and streaming added in later tasks).

> **Status:** the API contract is defined and validated. `POST /triage`
> currently returns a **deterministic mock response**. Real LLM provider
> integration is introduced in later tasks.

## Project structure

```text
app/
├── main.py            # FastAPI app
├── api/
│   └── routes.py      # HTTP routes
└── models/
    ├── requests.py    # TriageRequest
    └── responses.py   # Severity, TriageResponse
tests/
```

## Setup (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
uvicorn app.main:app --reload
```

Interactive docs: http://localhost:8000/docs

## Test

```powershell
python -m pytest
```

## API

### Health

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

### Triage

```http
POST /triage
Content-Type: application/json
```

Request:

```json
{
  "log": "ERROR database connection refused",
  "metadata": {
    "service": "payment-service",
    "environment": "production"
  }
}
```

Response (`200 OK`):

```json
{
  "category": "database",
  "severity": "high",
  "likely_cause": "Database connection refused",
  "suggested_next_step": "Verify database availability and network connectivity"
}
```

#### Request constraints

| Field      | Required | Rules |
|------------|----------|-------|
| `log`      | yes      | String, 1–10,000 characters, must not be empty or whitespace-only. Never truncated. |
| `metadata` | no       | Object of string keys to string values. At most 10 entries; keys 1–64 characters, values up to 256 characters. |

Unknown fields in the request body are rejected.

The 10,000-character log limit keeps future prompt size, cost and latency
bounded while still fitting a typical stack trace or log excerpt.

#### Response fields

| Field                 | Type   | Notes |
|-----------------------|--------|-------|
| `category`            | string | Non-empty, up to 64 characters. |
| `severity`            | enum   | One of `low`, `medium`, `high`, `critical`. |
| `likely_cause`        | string | Non-empty. |
| `suggested_next_step` | string | Non-empty. |

#### Validation behavior

Invalid requests return `422 Unprocessable Entity` with FastAPI's standard
error body, for example:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "log"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

Validation happens before any handler logic runs, so invalid input will never
reach an LLM provider. Note that the default 422 body echoes the offending
input back to the caller.

#### Current mock behavior

Every valid `POST /triage` request returns the same fixed response shown above.
The mock is built with `TriageResponse`, so it passes the same validation that
real LLM output will pass later. The request payload is not logged or stored.