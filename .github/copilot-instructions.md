# Sprint workspace instructions

This repository contains an existing application in `frontend` and `backend`,
alongside reusable engineering assets in `prompts` and `docs`.

## Scope and preservation

- Read `SPRINT.md` and the relevant document in `docs` before implementation.
- Preserve existing work. Do not recreate or overwrite the saved prompt collection.
- Files in `prompts` are not automatically loaded as repository instructions.
  Read a particular prompt only when explicitly selected for the task.
- Keep product-specific code in the existing application directories. Do not add
  a second application scaffold or nonfunctional placeholder scripts.
- Follow existing patterns and make focused changes. Report blocked or unverified
  work explicitly; do not describe planned checks as completed.

## Safety and authorization

- The user confirmed repository ownership and authorized a private upload to
  `joanmoturi/response-commitment-tracker` on October 20, 2026. Real-data permission
  and spending authorization remain unconfirmed. Approval to edit files or push
  privately is not permission to spend, deploy, or publish publicly.
- Do not copy employer-confidential material or global work-specific instructions
  into this workspace. Never print or commit credentials, tokens, or private data.
- Do not inspect `.env` files, `.local` runtime data, or unrelated private files
  unless specifically required and authorized.
- Do not install dependencies, call paid providers, migrate databases, deploy,
  publish, push, or commit unless the current task authorizes that action.
- Use synthetic data for examples and evaluation. Treat model output as untrusted.

## Existing verification

Use existing dependencies; if missing, report the blocker instead of installing.
From `frontend`, the configured checks are:

```powershell
npm run typecheck
npm run lint
npm test
npm run build
```

From `backend`, use its existing virtual environment for local checks:

```powershell
.\.venv\Scripts\python.exe -m pytest -m "not postgres"
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy app
```

Run only checks appropriate to the change. PostgreSQL tests require an explicitly
approved disposable database and can destroy its schema. See `backend/README.md`
and `.github/workflows/ci.yml`; do not run or trigger CI merely for inventory.
