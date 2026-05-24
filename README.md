# Weblab

Weblab is a backend-first experimentation platform for product teams that need safe and deterministic A/B rollouts.

## Business Use Case

Teams need to answer product questions quickly without shipping one permanent experience to all users. This project provides a central Weblab service where teams can:

- define an experiment and ownership
- choose session-based or user-based stickiness
- publish traffic splits across supported treatments
- resolve a treatment consistently for every request

The platform is designed to support low-traffic teams first, then scale by configuration and infrastructure changes.

## Product Rules

### Allocation modes

- `session_based`: sticky key is `sessionId`
- `user_based`: sticky key is `userId|regionId|stamp`

### Supported treatments

- `C,T1`
- `C,T1,T2`

### Split validation

- If all percentages are `0`, resolution returns `null`.
- If any percentage is non-zero, the total must be `100`.

### Stable rollout behavior

Assignments use deterministic hash ranges so expansion and contraction are monotonic:

- `0 -> 10`: any first 10% slice is acceptable
- `10 -> 20`: original 10% stays, only next 10% is added
- `20 -> 15`: only top 5% of prior slice is removed

## Current Scope

In this repository phase:

- Azure Functions backend on Flex Consumption
- modular Bicep infrastructure in `backend/infra`
- minimal health endpoint for deployment smoke tests

Planned next:

- weblab CRUD and publish APIs
- deterministic resolve API with sticky assignment
- persistence layer and versioned configurations

## Repository Layout

```text
backend/
  infra/
    main.bicep
    modules/
    params/
  src/
    function_app.py
    host.json
    requirements.txt
  test.http
```

## Operational Docs

Backend deployment and testing runbooks are in `backend/README.md`.