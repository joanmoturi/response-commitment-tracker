# Security review

**Latest audit:** October 19, 2026

**Scope:** response-tracker feature reviewed before its initial product commit.

**Release decision:** NO-GO for production or real customer data. An unresolved
High advisory remains in frontend development tooling, and production access
controls, deployment hardening, and recovery testing are incomplete. This is
not a penetration test or production security certification.

## October 19 audit results

- Direct API checks use two independently registered accounts. Each sees only
  its own list/search results; cross-account reads, updates, and completion
  return 404 in both directions. Anonymous create/list/read/update/complete
  return 401. No delete route exists by design.
- Reviewed request validation, ownership-scoped queries and mutations,
  parameterized/escaped search, idempotency, database constraints, completion
  transitions, UTC deadline handling, frontend output rendering, bearer and
  refresh-token handling, CSRF/Origin checks, CORS, proxy configuration,
  errors/logging, security headers, and production settings.
- `uv audit --locked` found no known vulnerabilities in 62 resolved backend
  packages. `npm audit` initially reported critical `tinypool` and moderate
  `@vitest/mocker` advisories through Vitest 3.2.7. Updating Vitest to 5.0.4
  removed those findings. Five remaining npm entries trace to one High advisory
  affecting `braces` <=3.0.3, pulled through the development-only
  `eslint-config-next` / `fast-glob` / `micromatch` chain. The npm registry has
  no `braces` 3.0.4; the advisory lists no patched version. Downgrading the
  Next 16 lint config to 14.x is incompatible and was not attempted. This is
  not a demonstrated remotely reachable tracker runtime path, but the
  unresolved tooling advisory blocks production release until patched or
  formally risk-accepted.
- Duplicate local registration returns 409 `email_unavailable` while local
  signup is enabled. Production configuration now fails startup unless
  `LOCAL_REGISTRATION_ENABLED=false`, and the route returns 403 when disabled;
  local sign-in remains available. OIDC account enrollment still depends on
  the provider's allowed-user policy. Login/refresh/registration have no
  application-level rate limits; apply shared ingress limits before public
  exposure.
- Source inspection found labeled inputs, semantic headings/landmarks, status
  and alert roles, focus-visible styling, and responsive utility breakpoints.
  No browser automation, visual viewport review, screen-reader, or formal
  accessibility audit was run. No PostgreSQL migration, live OIDC interaction,
  TLS deployment, container-image scan, backup restore, or rollback drill was
  run. These are unverified, not passed.

## Evidence and controls checked

- Read the request router, schemas, SQLAlchemy model, migration, route
  registration, frontend contracts/forms/list, and existing bearer-auth
  dependency.
- Verified every request lookup and mutation scopes by the authenticated
  account. Tests cover cross-account list/read/update/complete denial.
- Verified request fields reject extras, enforce length/nonempty limits, and
  require timezone-aware deadlines. FastAPI's existing validation handler
  avoids reflecting submitted values in validation errors.
- Verified SQL values are bound through SQLAlchemy; search escapes wildcard
  characters. Request text is rendered as React text, not injected HTML.
- Verified status and completion consistency constraints, idempotent creation
  per account, and conditional one-way completion.
- Ran API, migration-rendering, frontend date-boundary, and pagination tests;
  ran a synthetic Uvicorn workflow against a temporary SQLite database; see
  `testing-strategy.md` and `../SPRINT.md`.

## Independent review dispositions

A read-only independent review reported these concrete implementation issues:

| Observation | Disposition |
| --- | --- |
| A same-key insert racing another request could expire the authenticated user object during rollback | Fixed by capturing the account ID before the transaction; a test injects the competing insert and verifies replay recovery |
| Editing an unrelated field could shift a deadline during a daylight-saving overlap | Fixed by preserving the original UTC instant when the local deadline is unchanged and rejecting ambiguous/nonexistent new local times; frontend tests cover both |
| Completing the last item on a later page could strand the list | Fixed by clamping the current page to the new result count; pagination tests cover removal of a last-page item |
| No delete route or UI | Deliberately excluded by the approved MVP scope; the product has no destructive request operation, so confirmation is not applicable |

No unresolved feature-specific vulnerability was confirmed in the reviewed
scope. No files were changed by the independent reviewer.

## Remaining risks and unverified areas

- Apply ingress/shared rate limits to login, registration, refresh, and
  sensitive API calls before public exposure. Restrict OIDC enrollment to the
  intended population if OIDC is enabled.
- Production registration policy, verified-email enrollment, password recovery,
  MFA/OIDC policy, complete CSP/HSTS, TLS ingress, secret management, backup
  configuration, and retention controls remain deployment gates documented in
  the root README.
- Local bearer, refresh-cookie, logout, Origin/CSRF, and auth configuration
  paths were reviewed and tested. Live OIDC-provider behavior was not tested;
  the inherited agent and vector-document feature implementations were not
  included in this tracker release audit.
- The npm audit still reports High `CVE-2026-93687` / `GHSA-vfj7-8cjw-p6xm`
  for the `braces` development-tooling dependency; no patched release was
  available. A PostgreSQL runtime
  migration, browser end-to-end/accessibility test, production deployment,
  backup restore drill, and rollback test were not performed.
- The product stores owner names/contacts as user-entered text. Data retention,
  export, and deletion policies need a decision before real customer data is
  used.
- Shared-team authorization is not implemented; request data is private to one
  authenticated account.

Do not expose this pilot publicly or use real customer data until the applicable
deployment and data-handling gates are resolved.
