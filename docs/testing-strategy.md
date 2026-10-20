# Testing strategy

## Verified test layers

- **Backend API integration:** FastAPI requests through an ASGI test client,
  isolated SQLite database, and real SQLAlchemy persistence. The request tests
  cover account isolation, input validation, search escaping, pagination,
  owner/deadline updates, overdue boundaries, completion, repeat transitions,
  response recording, and duplicate-submission idempotency.
- **Migration rendering:** Alembic offline SQL generation checks that the
  existing PostgreSQL/pgvector migration chain includes migration `0002` and
  the request-table constraints.
- **Frontend quality:** TypeScript type checking, ESLint, and existing Vitest
  API-client tests. The production Next.js build verifies compilation and
  prerendering.

## Commands

Run from the repository root in PowerShell:

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m pytest -m "not postgres"
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy app
```

```powershell
Set-Location frontend
npm run typecheck
npm run lint
npm test
npm run build
npm audit --omit=dev
npm audit --audit-level=moderate
```

```powershell
Set-Location backend
uv audit --locked
```

## Limits

- No browser automation or end-to-end browser journey test is configured.
- No PostgreSQL server migration or live database integration was run during
  this task; `pytest -m postgres` requires an explicitly approved disposable
  database and may migrate it down to base.
- Tests use synthetic accounts and requests. They do not validate customer
  demand, production deployment, backup recovery, multi-user team behavior, or
  third-party services.

## Results for the response-tracker change

Final post-change verification on October 16, 2026:

- Backend `pytest -m "not postgres"`: **53 passed, 1 deselected**. The
  deselected test requires PostgreSQL.
- Backend Ruff check, Ruff format check, and mypy: **passed**.
- Frontend typecheck and lint: **passed**.
- Frontend Vitest: **13 passed** across 3 files.
- Frontend production build: **passed**.
- Runtime smoke: a Uvicorn API instance backed by an isolated temporary SQLite
  database completed registration, request creation, idempotent replay,
  overdue filtering, and completion. The temporary database was removed.
- Built frontend server: served the Response Tracker page with HTTP 200; the
  server was stopped after the check.
- The backend emitted an existing Authlib deprecation warning for its httpx
  integration. No dependency was changed to address it.

The final record is also in `../SPRINT.md`. These results do not validate a
live PostgreSQL migration, browser journey, remote deployment, or recovery.

## Final release audit - October 19, 2026

- Backend `.\.venv\Scripts\python.exe -m pytest -m "not postgres"`:
  **56 passed, 1 deselected**. The expanded direct API checks cover anonymous
  operation denial, bidirectional two-account list/search/read/update/complete
  isolation, unknown IDs, and persisted completion. Python 3.14.4 was used.
- Backend `ruff check`, `ruff format --check`, and `mypy app`: passed after
  formatting the added tests. Authlib emitted its existing httpx deprecation
  warning.
- Frontend `npm run typecheck`, `npm run lint`, and `npm test`: passed;
  **13 Vitest tests across 3 files** on Vitest 5.0.4. `npm run build`: passed.
- `npm audit --omit=dev`: **0 vulnerabilities** in production frontend
  dependencies. Full `npm audit --audit-level=moderate` still exits nonzero
  with five High entries all attributable to one unpatched `braces` advisory
  in the development lint-tool dependency chain. Vitest 5.0.4 removed the
  previous Critical `tinypool` and Moderate `@vitest/mocker` advisories.
- `uv audit --locked`: **no known vulnerabilities** in 62 resolved backend
  packages. `pip-audit` was not installed; no package was installed to add it.
- `npm audit --omit=dev` passed with 0 production dependency vulnerabilities.
  Full `npm audit --audit-level=moderate` is expected to exit 1 until the
  upstream High `braces` advisory has a patched release or the dependency path
  is safely removed.
- A fresh temporary SQLite database and production standalone Next frontend
  were used for a same-origin API workflow. Passed: anonymous request 401,
  provider discovery, registration 201, cookie/CSRF refresh 200, create 201,
  same-key replay 200, overdue list, update and separate persisted GET, second
  account list isolation/read denial (404), completion 200 with persisted
  response, removal from overdue, repeated completion 409, logout 204, and
  post-logout refresh 401. Both servers were stopped, the temporary database
  removed, and ports verified released.
- PostgreSQL migration/integration, browser automation and formal
  accessibility testing, container image scanning, live OIDC, production
  deployment, backup/restore, and rollback remain unverified. SQLite
  `create_all` is development-only and is not evidence of PostgreSQL migration
  success.

These results do not override the NO-GO production decision in
`security-review.md` and `deployment.md`.
