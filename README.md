# Spa Manager API

Backend service for the Spa Manager application built with FastAPI. The project focuses on a clear modular structure, per-route files, and a flexible authentication middleware that enforces access tokens, hierarchical roles, and arbitrary scopes.

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The service exposes a handful of demonstration routes (public, appointments, clients, staff tooling) and an `/auth/token` endpoint that issues demo access tokens.

## Architecture

- `main.py` creates the FastAPI application via `app.main.create_app`.
- `app/core` contains the middleware, config helpers, and JWT utilities.
- `app/models` defines the Pydantic schemas shared across routers.
- `app/services` holds simple in-memory services that mock persistence.
- `app/routes` contains feature-specific routers; each file owns its routes.

## Authentication and Authorization

- Requests include an `Authorization: Bearer <token>` header with a one-hour JWT access token.
- `AuthMiddleware` decodes the token, attaches the authenticated user to `request.state.user`, and enforces:
  - Whether auth is required for the endpoint
  - The minimum role (1–5 hierarchy, see `Role` enum)
  - Optional scopes (strings, e.g., `appointments:write`)
- Endpoints declare their auth configuration with the `@auth_config(...)` decorator from `app.core.auth`.

The middleware can be bypassed per endpoint using `@auth_config(required=False)`.

## Environment Variables

Configure the following variables (defaults work for local development):

| Variable | Description |
| --- | --- |
| `APP_NAME` | Service title |
| `JWT_SECRET_KEY` | Secret used to sign JWTs |
| `JWT_ALGORITHM` | Signing algorithm (default `HS256`) |
| `JWT_EXPIRATION_MINUTES` | Access token lifetime (default 60) |

Create a `.env` file or export the vars before launching the server.

## Testing Tokens Quickly

Use the `/auth/token` endpoint with a JSON body:

```json
{
  "username": "owner",
  "password": "spa-owner"
}
```

Two other demo accounts: `manager`/`spa-manager`, `staff`/`spa-staff`. Each has different roles and scopes so you can see enforcement in action.

---

This scaffold is intentionally minimal yet extensible. Replace the in-memory services with real repositories, wire up persistence, and expand routers as your application grows.
