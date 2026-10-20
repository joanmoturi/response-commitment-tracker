# Deployment and operations

**Release audit (October 19, 2026): NO-GO for production or real customer data.**
The application and local Compose path exist, but this is not a production-ready
deployment. The unresolved High frontend development-tool advisory, ingress
rate limits and identity-provider enrollment policy, missing public TLS/security
controls, and untested PostgreSQL/recovery procedures must be resolved or
explicitly risk-accepted before release. See `security-review.md`.

## Current deployment state

The existing Docker Compose setup is a local pilot path, not a public production
configuration. Compose binds the database, backend, and frontend ports to
loopback. No remote environment was configured or deployed; no hosting
provider, DNS, TLS ingress, external monitoring, or ongoing cost has been
selected or verified.

## Local PostgreSQL deployment path

1. Install Docker Desktop with Compose and configure the root `.env` from
   `.env.example` using unique generated secrets. Keep `.env` untracked.
2. Use the existing compose stack:

   ```powershell
   docker compose up --build -d
   docker compose ps
   docker compose logs --tail 100 migrate
   docker compose logs --tail 100 backend
   ```

3. Confirm the migration service completes, then check
   `http://localhost:8000/health/ready` and open `http://localhost:3000`.
4. Configure production-only values, OIDC or a controlled registration policy,
   HTTPS, database access, ingress limits, backups, retention, and monitoring
   before any public exposure. The starter's defaults are not an internet-facing
   production profile.

Compose runs `alembic upgrade head` in a separate migration service before the
API starts. The request table is added by migration `0002`; existing request
records are not created automatically. Local SQLite development uses
`Base.metadata.create_all` and does not provide a schema migration history.

## Required configuration and external prerequisites

See `.env.example`, the root README, and `backend/README.md` for the exact
configuration contract. At minimum, a production-like deployment needs a strong
independent `JWT_SECRET`, a PostgreSQL `DATABASE_URL` with pgvector installed
for the inherited vector endpoints, correct frontend/API origins, secure
cookies, and a TLS reverse proxy. OpenAI and OIDC settings are optional for the
response tracker; configuring them enables inherited agent/auth features and
requires separate provider and data-policy approval.

The checked-in Compose/example defaults are development settings
(`ENVIRONMENT=development`, `COOKIE_SECURE=false`, localhost HTTP); do not use
them for a public deployment. Production requires
`ENVIRONMENT=production`, `COOKIE_SECURE=true`, HTTPS `FRONTEND_URL`,
HTTPS-only `CORS_ORIGINS` containing that origin, a `JWT_SECRET` of at least
32 characters, and secrets stored outside the repository. `POSTGRES_PASSWORD`
and `JWT_SECRET` are required by Compose; OIDC values must be complete and
match the registered callback if OIDC is the chosen sign-in policy.
`LOCAL_REGISTRATION_ENABLED=false` is also required in production; startup fails
closed otherwise, while existing local users can still sign in. Restrict OIDC
enrollment to the intended population. Apply shared rate limits at trusted
ingress; do not rely on per-process limits.

Do not expose the app publicly without rate limiting, secret management,
database/network restrictions, TLS, retention decisions, and monitoring.
Production registration policy, verified email, password recovery, and MFA are
existing documented security gates.

## Backup, recovery, and rollback

- Configure encrypted, access-controlled PostgreSQL backups using the selected
  hosting provider's supported backup process. Keep backups separate from the
  database account and define retention before using real data.
- Restore a backup to a disposable database and verify both schema and request
  records before claiming recovery readiness. This restore drill has **not**
  been run.
- Migration `0002` is additive. Do not downgrade it after creating requests:
  its downgrade drops `tracked_requests` and permanently removes those records.
  Preserve data with a verified backup and coordinate application/database
  rollback; no production rollback has been tested.
- Compose `docker compose down` preserves the named database volume. Removing
  volumes is destructive and is not part of the routine stop procedure.

## Health checks and release limits

Use `/health/live` for process liveness and `/health/ready` for schema/database
readiness. The production build and offline migration SQL are locally verified;
a real PostgreSQL migration, remote deployment, TLS, backups, monitoring, and
rollback remain unverified. No claim of production deployment or recovery
readiness is made.
