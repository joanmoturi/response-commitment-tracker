# 30-day AI-assisted software engineering sprint

## Outcomes

Ship one useful product, develop reusable engineering assets, practice bounded
agent orchestration, and deliver a credible demo. The existing application is
the foundation for the selected private-account response-tracker pilot; customer
validation remains open.

## Status conventions

- Complete: the stated outcome was observed, with its limitations recorded.
- Pending: proposed work, not evidence of implementation or validation.
- Blocked: work cannot proceed; record the specific missing prerequisite.

Day numbers are the user's sprint labels, not inferred calendar dates. Discovery
and setup were discussed on October 15, 2026; later dates must be recorded from
actual work. An approved schedule is not proof of ownership or spending permission.

## Proposed sequence and daily outcomes

| Day | Intended outcome | Status / observed outcome |
| --- | --- | --- |
| 1 | Environment discovery and safety boundaries | Complete: local tools and CLI mechanisms inventoried; no product selected |
| 2 | Preserve prompts and prepare the sprint workspace | Complete: six existing prompts located; approved documentation setup completed; no application changes |
| 3 | Identify target user and concrete problem | Complete as a prompt-supplied hypothesis; customer evidence remains absent |
| 4 | Select the smallest useful product and non-goals | Complete: private per-account response tracker; shared teams deferred |
| 5 | Confirm acceptance criteria, data boundaries, and authorization | Complete for local edits/checks and synthetic tests; external actions excluded |
| 6 | Establish application/check baseline using permitted local execution | Complete: backend and frontend baseline checks passed |
| 7 | Record architecture choice and week-one scope | Complete: existing stack retained; private account isolation and owner text |
| 8 | Plan the first end-to-end vertical slice | Complete: pilot workflow implemented and final checks passed |
| 9 | Implement the first slice with focused tests | Complete: API/UI and focused tests delivered |
| 10 | Independently review the slice and resolve defects | Complete: three review defects fixed; delete excluded by scope |
| 11 | Check the workflow against realistic synthetic examples | Complete: synthetic API workflow and edge cases exercised |
| 12 | Extract one reusable improvement from repeated work | Pending |
| 13 | Add important failure-case coverage | Complete: validation, idempotency race, transitions, deadlines covered |
| 14 | Demonstrate the first useful workflow and adjust scope | Complete locally: runtime smoke passed; no user demo |
| 15 | Identify the largest remaining user-value gap | Pending |
| 16 | Implement the next agreed increment | Pending |
| 17 | Exercise bounded implementation/review orchestration | Pending |
| 18 | Evaluate an AI engineering asset against fixed examples | Pending |
| 19 | Review reliability, recovery, and failure reporting | Complete for feature scope; production recovery remains untested |
| 20 | Perform a scoped security review | Complete: feature review documented; broader audit remains open |
| 21 | Resolve or document review findings | Complete: in-scope defects fixed; release gates documented |
| 22 | Simplify product flow and remove unnecessary scope | Complete: private-account scope; team collaboration deferred |
| 23 | Rehearse setup using documented steps | Pending |
| 24 | Verify core workflow and regression checks | Complete: backend/frontend checks passed; PostgreSQL excluded |
| 25 | Prepare the demo narrative and permitted sample data | Pending |
| 26 | Rehearse the demo and capture gaps | Pending |
| 27 | Fix demo-blocking defects and disclose limitations | Pending |
| 28 | Prepare release/demo notes using the existing release prompt | Pending |
| 29 | Freeze scope and verify the final demo baseline | Pending |
| 30 | Deliver the demo and write the sprint retrospective | Pending |

## Current evidence and open decisions

- Application code remains in `frontend` and `backend`; prompts remain separate.
- Initial setup did not run application tests, install packages, or validate
  deployment; the dated implementation follow-up below records later checks.
- Product scope is the user-approved private-account tracker pilot. Repository
  ownership was confirmed on October 20, 2026, with a private upload authorized to
  `joanmoturi/response-commitment-tracker`, retaining existing Git history and
  leaving `ai-agent-boilerplate` unchanged. Customer evidence, permitted real
  data, demo audience, and daily time budget remain unconfirmed. Paid services,
  public publication, and deployment are not authorized.
- Use only synthetic data until real-data permission and retention rules are
  established.
- Update each day's outcome with evidence when work happens; do not pre-mark
  future work complete. Record blockers here and revise the sequence deliberately.
- Keep usage evidence in `CREDIT-LOG.md`, product decisions in
  `docs/product-spec.md`, and actual review evidence in `docs/security-review.md`.

### Product implementation follow-up - October 16, 2026

- **State:** Complete for the selected technical MVP; market validation and
  production deployment remain incomplete.
- **Planned deliverable:** Implement and verify the first useful response-
  commitment workflow in the existing application.
- **Product decision:** User selected the response-tracking candidate and
  authorized local source edits and existing non-destructive checks. A read of
  existing sprint documentation found no interviews, customer records, or
  demand evidence. The prompt describes a plausible problem, so the approved
  scope is a pilot MVP, not a commercially validated product. The user accepted
  private per-account records with owner names/contacts; shared team membership
  and invitations are deferred.
- **Actual deliverable and evidence:** Added persistent request records,
  migration `0002`, authenticated account-scoped API operations, idempotent
  creation, update/reassignment, search/filter/pagination, derived overdue
  state, optional completion response, and a responsive tracker UI. Product,
  architecture, testing, security, deployment, backend API, and root README
  documentation were updated. A temporary SQLite/Uvicorn smoke completed
  register, create, replay, overdue-list, and completion; the built frontend
  server returned HTTP 200. Temporary DB and servers were removed. The existing
  agent/vector endpoints and saved prompts were preserved.
- **Test/check results:** Backend
  `.\.venv\Scripts\python.exe -m pytest -m "not postgres"`: 53 passed, 1
  deselected; Ruff check/format and mypy passed. Frontend typecheck and lint
  passed; Vitest: 13 passed across 3 files; production build passed.
  PostgreSQL runtime tests, browser E2E, and remote deployment were not run.
  The backend emitted an existing Authlib httpx deprecation warning.
- **Independent review:** A read-only review reported an idempotency conflict
  recovery issue, a daylight-saving deadline edit issue, a last-page navigation
  issue, and missing delete functionality. The first three were fixed and
  verified by a competing-insert test and focused frontend tests. Delete is
  explicitly outside the approved MVP; no destructive operation is provided.
  No unresolved feature-specific Critical or High vulnerability was confirmed.
- **Blockers and limitations:** No customer interviews or real pilot evidence;
  no shared team collaboration; no live PostgreSQL migration, production
  deployment, dependency advisory scan, browser journey, backup/restore drill,
  or rollback test. Existing production security gates remain; see
  `docs/security-review.md` and `docs/deployment.md`.
- **Next action:** Validate the workflow with permitted prospective users and
  obtain approval for a disposable PostgreSQL integration environment before
  claiming production deployability.
- **Usage/outcome log reference:** No reliable authorized usage or cost
  measurement was available; no paid provider calls or external actions were
  performed. `CREDIT-LOG.md` was not changed because no measured amount was
  available.

### Independent final release audit - October 19, 2026

- **Decision:** NO-GO for production deployment or real customer data. The
  local Compose stack is not a public production configuration, and no
  customer validation or external deployment was performed.
- **Audit scope and fixes:** Re-reviewed request API/account scoping, auth and
  session boundary, request validation/business rules, UI contracts/rendering,
  persistence/migration assets, deployment configuration, and existing
  security headers/logging. Added symmetric two-account direct-API
  non-enumeration checks, anonymous-operation denial tests, unknown-ID cases,
  and a persisted-completion assertion. Production configuration now fails
  unless `LOCAL_REGISTRATION_ENABLED=false`; disabled signup returns 403,
  `/auth/providers` reports signup availability, and the UI hides its signup
  toggle. Local development remains enabled. Local frontend/backend commands
  bind to loopback; root README paths are portable.
- **Verification:** Backend 56 passed / 1 PostgreSQL test deselected; Ruff
  check/format and mypy passed. Frontend typecheck/lint passed, Vitest 13 passed
  across 3 files with Vitest 5.0.4, and production build passed. A same-origin
  standalone Next -> FastAPI workflow on a temporary SQLite database passed
  auth/CSRF refresh, create/idempotent replay, overdue/update/persistence,
  second-account isolation, completion, logout, and expected HTTP statuses.
  Temporary data and owned servers were cleaned up.
- **Dependency review:** `uv audit --locked` found no known backend dependency
  issues in 62 packages; `npm audit --omit=dev` found zero production frontend
  advisories. Updating Vitest removed two Critical `tinypool` and one Moderate
  `@vitest/mocker` audit paths. Full npm audit still reports five High entries
  for the single unpatched `braces` CVE-2026-93687 in the development-only
  Next lint dependency chain. The advisory has no patched release; downgrading
  Next to v14 is not compatible and was rejected. This remaining toolchain risk
  blocks release pending an upstream patch or explicit risk acceptance.
- **Not verified:** No live PostgreSQL migration, browser visual/accessibility
  or automated E2E, live OIDC provider, production TLS deployment, container
  image scan, rate-limit behavior, backup/restore, rollback, or customer
  validation. Account lifecycle, retention/export/deletion, and shared-team
  needs also require decisions before real users rely on the product.
- **Next actions:** Resolve or formally accept the unpatched build-tool
  advisory; configure restricted identity enrollment and shared ingress
  protections; then validate production database migration, monitoring, and
  restore/rollback before a controlled real-user pilot.
