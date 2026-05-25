# Backend README

This document covers backend infrastructure deployment, code deployment, and API testing.

## What Is In Backend

- `infra/`: Bicep templates and environment parameter files
- `src/`: Azure Functions Python app
- `test.http`: simple HTTP smoke test requests

## Prerequisites

- Azure CLI logged in to the correct subscription
- Azure Functions Core Tools 4+
- Python virtual environment available in `backend/src/.venv`
- Access to create/update resources in the target resource group

## Environment Conventions

Test environment defaults:

- Resource group: `weblab-test-rg`
- Function app: `weblab-test-func`
- Plan: `weblab-test-plan`
- App Insights: `weblab-test-appi`
- Log workspace: `weblab-test-log`

Production follows the same pattern with `prod`.

## Deploy Infrastructure

Run from repository root.

1. Set subscription

```bash
az login
az account set --subscription 4d25d429-4d44-4b9a-b66f-6de9b83e0190
```

2. Create resource group (test)

```bash
az group create --name weblab-test-rg --location eastus
```

3. Deploy Bicep (test)

```bash
az deployment group create \
  --resource-group weblab-test-rg \
  --template-file backend/infra/main.bicep \
  --parameters backend/infra/params/test.bicepparam
```

Optional validation before deploy:

```bash
az deployment group validate \
  --resource-group weblab-test-rg \
  --template-file backend/infra/main.bicep \
  --parameters backend/infra/params/test.bicepparam
```

## Deploy Function Code

Run from `backend/src`.

1. Create and activate virtual environment

```bash
cd backend/src
python -m venv .venv
# PowerShell
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies (if needed)

```bash
pip install -r requirements.txt
```

3. Publish function app (single command)

```bash
func azure functionapp publish weblab-test-func --python
```

## Testing

Open `backend/test.http` and run:

- `GET https://weblab-test-func.azurewebsites.net/api/health`

## API Endpoints (MVP)

All routes are anonymous for now and served under `/api`.

- `POST /api/weblabs`
- `POST /api/weblabs/validate-id`
- `GET /api/weblabs`
- `GET /api/weblabs/{weblabId}`
- `PUT /api/weblabs/{weblabId}/allocation`
- `POST /api/weblabs/{weblabId}/getTreatment`

Validate weblab id payload example:

```json
{
  "weblabId": "TEST_WEBLAB"
}
```

Weblab id rules:

- must be unique
- must be uppercase
- no spaces
- allowed characters: `A-Z`, `0-9`, `_`, `-`

Create payload example:

```json
{
  "weblabId": "TEST_WEBLAB",
  "name": "checkout-hero-test",
  "assignmentMode": "session_based",
  "treatmentSet": "C,T1"
}
```

Update allocation payload example:

```json
{
  "regionId": "US",
  "stamp": "S1",
  "splits": {
    "C": 80,
    "T1": 20
  }
}
```

getTreatment payload examples:

```json
{
  "sessionId": "session-123",
  "regionId": "US",
  "stamp": "S1"
}
```

```json
{
  "userId": "u-1",
  "regionId": "US",
  "stamp": "S1"
}
```

## Local Development and Tests

From `backend/src`:

```bash
python -m venv .venv
# PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
func start
```

## Database Notes

The app defaults to an in-memory repository for quick MVP iteration.

To enable PostgreSQL repository wiring, set:

- `WEBLAB_DATABASE_URL`

The initial schema for `weblabs`, `weblab_versions`, and `weblab_audit` is in `backend/src/sql/schema.sql`.