# Product specification

**Status:** Pilot MVP selected and implemented; customer demand remains unvalidated.

## Product hypothesis

Small B2B service teams may lose track of requests, who is expected to respond,
and when a response is due. A focused tracker may help a coordinator keep those
commitments visible and close the loop. This is a hypothesis from the user-
provided product prompt, not a finding from customer research.

## Target user and buyer

- **Target user hypothesis:** A coordinator or team lead at a small B2B service
  team who follows up on customer or partner requests.
- **Buyer hypothesis:** The team lead or small-business owner who is accountable
  for response reliability.
- **Evidence:** The product prompt supplies this candidate audience and problem.
  No interviews, customer records, usage telemetry, or willingness-to-pay
  evidence have been collected.

## Primary workflow

1. Sign in to a private account.
2. Record the response or action needed, its details, an owner name/contact, and
   a timezone-aware deadline.
3. Search, filter, and review open, overdue, completed, or all requests.
4. Change the owner or deadline while the request is open.
5. Record an optional response and complete the request.
6. Confirm completed requests no longer appear overdue.

## Product decision and trade-offs

The user selected this product and approved a private per-account pilot MVP.
Requests are isolated to the authenticated account; the assigned owner is a
name/contact string, not an application user. The current version does not share
requests with a team or give assigned owners access.

This keeps the first workflow within the existing per-user authentication model
and avoids inventing invitations, membership, or team authorization without
discovery evidence. The trade-off is substantial: it supports a coordinator
tracking work on behalf of a team, not real-time multi-user collaboration.
Shared team workspaces should be considered only after user validation and an
explicit access-control design.

## Alternatives and differentiation

Likely alternatives include spreadsheets, shared inboxes, and general-purpose
task boards. This list is an unresearched hypothesis; no current competitive
analysis was performed. The differentiation hypothesis is a small workflow
centered on response ownership and deadline state rather than broad project
management. It is not validated.

## In scope

- Authenticated, account-private request creation and editing.
- Required request details, free-form owner name/contact, and deadline.
- Server-side search, filtering, sorting, and bounded pagination.
- Overdue calculation from the current UTC time and deadline; completed requests
  are never overdue.
- Optional response capture when completing an open request.
- Input validation, clear empty/error/loading states, and responsive layout.
- Idempotent request creation so a retried submission does not create a
  duplicate.
- Database migration and focused API tests.

## Out of scope

- Shared team workspaces, invitations, assigned-user accounts, roles, or
  cross-account access.
- Email, messaging, calendar, or AI integrations.
- Billing, analytics, mobile applications, and enterprise administration.
- Deleting requests; the MVP has no destructive request action.
- Public deployment, commercial readiness, or regulatory certification.

## Acceptance criteria

- A signed-in user can create and later retrieve a persistent request with an
  owner and timezone-aware deadline.
- A different account cannot list, read, update, or complete that request.
- Open, overdue, completed, and all views use persisted records and server-side
  filtering; search and pagination are bounded.
- An open request can be reassigned or have its deadline changed.
- Overdue is derived from `deadline < now` and open status; an exact-boundary
  deadline is not overdue, and completed requests are not overdue.
- A request can be completed once with an optional response; repeated completion
  and edits after completion are rejected.
- Retrying request creation with the same per-account submission key returns
  the original record rather than creating a duplicate.
- Invalid input is rejected without echoing submitted values, and the UI
  displays actionable loading, empty, and error states.
- The migration applies on a fresh database through the existing migration
  chain; the local SQLite development server creates the new table.

See `testing-strategy.md` for verified test coverage and limitations.

## Remaining validation

- No customer interviews, workflow observations, pilot usage, or demand signals.
- No evidence that current alternatives are inadequate or that this workflow is
  differentiated.
- Target buyer, response-volume frequency, deadline conventions, retention
  needs, collaboration requirements, and willingness to pay are unknown.
- Only synthetic test data is used. The product is not commercially validated.
