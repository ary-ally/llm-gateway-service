# Aegis Core — LLM Gateway Service

A FastAPI service exposing an API for triaging infrastructure logs.

> **Status:** the API contract (T02) is implemented. `POST /triage` currently
> returns a **deterministic mock response**; no LLM provider is called yet.

Requires Python 3.11+.

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

### `GET /health`

```json
{
  "status": "ok"
}
```

### `POST /triage`

```http
POST /triage
Content-Type: application/json
```

Request:

```json
{
  "log": "Database connection timeout after 30 seconds",
  "metadata": {
    "service": "payments",
    "environment": "production"
  }
}
```

Response (`200 OK`):

```json
{
  "category": "database",
  "severity": "high",
  "likely_cause": "Database connection pool exhaustion",
  "suggested_next_step": "Inspect active connections and pool utilization"
}
```

#### Request constraints

| Field      | Required | Rules |
|------------|----------|-------|
| `log`      | yes      | String, 1–10,000 characters; empty and whitespace-only values are rejected. Never truncated or modified. |
| `metadata` | no       | Object with string keys and string values. At most 10 entries; keys 1–64 characters; values up to 256 characters. |

Unknown fields in the request body are rejected.

The 10,000-character limit fits a typical stack trace or log excerpt while
keeping request size bounded.

#### Response fields

| Field                 | Type   | Notes |
|-----------------------|--------|-------|
| `category`            | string | Non-empty, up to 64 characters. |
| `severity`            | enum   | One of `low`, `medium`, `high`, `critical`. |
| `likely_cause`        | string | Non-empty. |
| `suggested_next_step` | string | Non-empty. |

#### Validation

Invalid requests return `422 Unprocessable Entity` with FastAPI's standard
error body. The default error body echoes the offending input.

#### Current behavior

Every valid request returns the fixed mock response shown above. The request
payload is not logged or stored.