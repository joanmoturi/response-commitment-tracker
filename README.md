# Response Commitment Tracker

An authenticated pilot MVP for small B2B service coordinators to track response
requests, owner names, deadlines, and completion. Requests are private to the
signed-in account; assigned owners are free-form names or contacts, not shared
application users. Team workspaces and customer validation are not yet included.

The repository retains the existing FastAPI / Next.js foundation, including its
agent and vector-document endpoints. Those inherited capabilities are not part
of the selected tracker workflow.

This project is maintained separately as `joanmoturi/response-commitment-tracker`;
the original `ai-agent-boilerplate` repository is not its publishing destination.

**Current status:** private-account pilot implementation is present, but the
October 19 release audit is **NO-GO for production or real customer data**.
Customer demand is unvalidated, an unpatched high-severity development-tool
dependency advisory remains, and production controls/recovery are unverified.
See `docs/security-review.md` and `docs/deployment.md`.

## Quick start (PowerShell)

### Without Docker: local SQLite development

Run each command in a separate PowerShell window and leave both windows open:

```powershell
Set-Location .\backend
# First-time dependency setup: uv sync --frozen --extra dev
.\.venv\Scripts\python.exe -m scripts.dev_server
```

```powershell
Set-Location .\frontend
# First-time dependency setup: npm ci
npm run dev
```

Run those commands from the repository root in separate PowerShell windows.
Visit `http://localhost:3000` (use `localhost`, not `127.0.0.1`, for browser
authentication). The development launcher creates an ignored `.local` directory
containing the persistent SQLite database and a stable randomly generated JWT
secret. It never runs in the production image. SQLite is **development-only**:
document embedding/search endpoints explicitly require PostgreSQL/pgvector.
Local schema creation is not a migration system; existing SQLite databases will
need deliberate reset or migration when the model schema changes.

To enable AI, configure `OPENAI_API_KEY` in the root or backend `.env`, then
restart the backend. Without a key, registration/login work but AI execution
returns `openai_not_configured`. Stop each server with Ctrl+C.

### With Docker: PostgreSQL and pgvector

Install Docker Desktop with Compose, then:

```powershell
Copy-Item .env.example .env
python -c "import secrets; print('POSTGRES_PASSWORD=' + secrets.token_hex(24)); print('JWT_SECRET=' + secrets.token_hex(32))"
# Put the generated values in .env and set OPENAI_API_KEY to run the agent.
docker compose up --build -d
```

Visit `http://localhost:3000`. Create an account with a password of at least 12
characters. The backend API documentation is at `http://localhost:8000/docs`.
Authentication works without an OpenAI key; agent execution explicitly reports
that the provider is unavailable rather than returning a fabricated answer.

The generated database password is URL-safe. If you use a different password,
URL-encode it when constructing a database connection URL. Do not check `.env`
into source control.

## Architecture

```text
Browser
  -> Next.js same-origin /api/v1 proxy
    -> FastAPI routers + validated request/response schemas
      -> injected authentication / agent / LLM services
        -> request-scoped async SQLAlchemy sessions -> PostgreSQL
        -> bounded structured-output decisions -> allowlisted tool -> next step
```

The frontend is feature-oriented: `src/features/auth`, `src/features/agent`,
shared `src/components`, and validated contracts / HTTP client in `src/lib`.
Runtime response validation complements strict TypeScript, preventing unchecked
API payloads from silently reaching UI components.

Access tokens remain in memory, not local storage. Refresh tokens are opaque,
stored hashed in the database, rotated through HttpOnly cookies, and guarded by
Origin checks plus a readable `csrf_token` cookie / `X-CSRF-Token` header pair
for refresh and logout. Concurrent requests in one browser client share a refresh promise;
requests retry once after a 401, never indefinitely. Cookies and authentication
responses must never be cached by a proxy.

The agent executes synchronously within a bounded request and stores run state.
Structured model outputs are parsed into Pydantic schemas before routing a step;
generated code and arbitrary network tools are not executed. Persistence is not
a durable worker queue: a process crash may interrupt an active run. Before
shipping long-running workloads, move execution to a durable queue / worker with
leases, idempotency, cancellation, and a recovery policy.

## Authentication

Local login and registration are enabled for development. Optional OIDC uses
provider discovery, validated identity tokens, and authorization-code callbacks.
Register the exact redirect URI with your identity provider:

```text
http://localhost:3000/api/v1/auth/oidc/callback
```

Set `OIDC_ISSUER`, `OIDC_CLIENT_ID`, `OIDC_CLIENT_SECRET`, and
`OIDC_REDIRECT_URI` in `.env`. The frontend displays the OIDC button only when
the backend reports it enabled. Callback login sets a refresh cookie and
redirects to the app; no access token is exposed in a URL.

For production, keep browser API traffic and callbacks on a single public origin
via the Next proxy or ingress. Set `FRONTEND_URL`, `CORS_ORIGINS`, and the OIDC
redirect URI to that origin. Do not link local and OIDC accounts merely because
their email addresses match.

`LOCAL_REGISTRATION_ENABLED` defaults to `true` for local development. Production
configuration must explicitly set it to `false`; startup fails closed otherwise.
Existing local-password users can still sign in, and OIDC provisioning remains
available when configured. If public self-registration is required, design and
review that policy separately rather than exposing this local endpoint.

## API contract

All application routes are under `/api/v1`.

| Route | Behavior |
| --- | --- |
| `POST /auth/register` | `{email, password}`; create local account and session |
| `POST /auth/login` | `{email, password}`; issue access token and refresh cookie |
| `POST /auth/refresh` | Rotate cookie; return access token and user |
| `POST /auth/logout` | Revoke refresh session and clear cookie |
| `GET /auth/me` | Bearer-authenticated current user |
| `GET /auth/providers` | Available local / OIDC login and registration options |
| `GET /auth/oidc/login` | Start configured OIDC authorization flow |
| `GET /auth/oidc/callback` | Validate callback and establish application session |
| `POST /agent/runs` | `{prompt}`; execute bounded agent and persist result |
| `GET /agent/runs/{id}` | Read a run belonging to the current user |
| `POST /requests` | Create a private response request with an idempotency key |
| `GET /requests` | List own requests; filter by status/search and paginate |
| `GET /requests/{id}` | Read own request; other accounts receive 404 |
| `PATCH /requests/{id}` | Update details, owner, or deadline while open |
| `POST /requests/{id}/complete` | Complete once and optionally record a response |
| `GET /health/live` | Process liveness (outside `/api/v1`) |
| `GET /health/ready` | Database readiness (outside `/api/v1`) |

Auth responses contain `{access_token, token_type: "bearer", user: {id, email}}`.
Run responses contain `{id, status, answer, error, steps}`. The frontend displays
explicit errors for failed runs, provider failures, network errors, and malformed
API responses.

## Frontend development

```powershell
Set-Location frontend
npm ci
npm run dev
```

The default proxy target is `http://127.0.0.1:8000`. Set the server-only
`BACKEND_INTERNAL_URL` environment variable to change it. Next.js rewrites are
resolved during the production build, so changing the production target requires
rebuilding the image. No secrets belong in `NEXT_PUBLIC_*` variables.

```powershell
npm run typecheck
npm run lint
npm test
npm run build
```

The API-client suite covers concurrent token refresh, retry bounds, response
validation, logout failures, session races, and network failures.

## Backend development and tests

```powershell
Set-Location backend
uv sync --frozen --extra dev
Copy-Item .env.example .env
# Set DATABASE_URL and JWT_SECRET in backend/.env before launching.
uv run alembic upgrade head
uv run uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
```

```powershell
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
uv run mypy app
```

The default API integration suite uses isolated SQLite databases and mocked LLM
responses. Set `TEST_POSTGRES_URL` to a disposable PostgreSQL database to run the
real migration / pgvector test; never point this test at production data.

GitHub Actions includes frontend checks and backend checks on Python 3.12 / 3.14
with an isolated pgvector PostgreSQL service. The workflow has been generated,
not executed on GitHub as part of this handoff.

## Containers and operations

Compose waits for PostgreSQL health, runs Alembic migrations once as a separate
service, then starts the API and frontend. Both application images run as
non-root users. The database persists in a named volume; ordinary
`docker compose down` does not delete it.

```powershell
docker compose ps
docker compose logs --tail 100 backend
docker compose run --rm migrate
docker compose down
```

Development ports bind to loopback. The database image includes pgvector;
the migration enables its extension. Use a managed PostgreSQL instance,
external secret storage, TLS ingress, and controlled migration credentials for
production rather than treating local Compose as an internet deployment.

## Production gates

This is a production-oriented foundation, not a certification of your deployment.
Before exposing it publicly:

- Set `ENVIRONMENT=production`, `COOKIE_SECURE=true`, strong independent secrets,
  HTTPS-only public origins, and a configured OIDC callback.
- Apply ingress rate limits for login, registration, refresh, and AI execution;
  add shared per-account AI budgets and quotas across API replicas.
- Add verified-email enrollment, password recovery, and MFA or require OIDC;
  restrict public registration according to your product's access policy.
- Set restrictive CSP and HSTS at TLS ingress. Next's base headers do not replace
  a complete deployment-specific CSP.
- Configure database backups, restore drills, pool sizing, schema migration
  approvals, dependency scanning, retention policies, and monitored alerts.
- Treat prompts and generated output as untrusted content. Review provider data
  processing terms and redact sensitive content from observability pipelines.
- Replace inline execution with durable workers when workloads outgrow the
  request budget; never claim that a persisted row alone provides crash recovery.

Use the committed frontend lockfile for reproducible installs. Backend dependency
and database integration instructions are documented alongside the backend.

## AI engineering sprint workspace

This repository also holds the reusable engineering assets and outcome records
for a 30-day AI-assisted software engineering sprint. Application code stays in
`frontend` and `backend`; the sprint assets do not create another application.
The selected flagship is a private-account response-tracker pilot; customer
validation remains incomplete.

| Location | Use |
| --- | --- |
| `prompts` | Existing reusable prompt collection; preserve the saved files |
| `docs/product-spec.md` | Selected pilot scope, assumptions, and acceptance criteria |
| `docs/architecture.md` | Workspace organization and documented application foundation |
| `docs/security-review.md` | Scoped feature review and remaining production gates |
| `docs/implementation-plan.md` | Setup, discovery, implementation, and demo gates |
| `SPRINT.md` | Proposed 30-day sequence, daily outcomes, and status |
| `CREDIT-LOG.md` | Manual authorization, usage evidence, and outcomes |
| `.github/copilot-instructions.md` | Persistent repository guidance for Copilot |

Start Copilot from this repository directory, not the home directory:

```powershell
# From the repository root
copilot
```

The CLI discovers recognized repository instruction files; a directory named
`prompts` is not automatically loaded. Use `/instructions` to inspect instruction
discovery. User-wide instructions can also apply, so repository guidance alone
does not isolate this workspace from global customization.

Select a saved prompt explicitly for a task, for example: "Read
`prompts/01-product-discovery.md` and use it to guide discovery only; do not modify
files." The saved collection also includes `00-operating-rules.md`,
`02-architect.md`, `03-implementer.md`, `04-reviewer.md`, and `05-release.md`.
Task instructions and tool permissions still determine what actions are allowed.

Use the existing verification commands and CI before adding shared scripts.
There is intentionally no root `scripts` directory until a concrete, working
helper is needed. The user confirmed repository ownership and authorized a private
GitHub upload on October 20, 2026. Real-data permission and spending authorization
remain unconfirmed; do not copy employer-confidential material into this workspace
or treat the private upload as permission to publish publicly, spend, or deploy.
