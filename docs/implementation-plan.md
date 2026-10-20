# Implementation plan

This plan preserves the existing application and prompt collection. A narrow
pilot MVP was selected by the user; demand remains unvalidated.

## 1. Finish workspace setup

- Preserve all six prompts and all existing application work.
- Add the approved sprint documents and repository instructions.
- Extend the existing README with navigation and prompt-use guidance.
- Check that edits stay within the approved paths; do not run application code,
  install dependencies, or create placeholder scripts for this documentation task.

## 2. Select the product

The user selected response-commitment tracking from the attached master prompt
and authorized local source edits and existing non-destructive checks. The
product spec records the supplied target/problem hypothesis and explicitly
marks customer evidence as absent. The existing application supports a
private-per-account pilot; shared teams, invitations, paid providers, deployment,
publishing, and spending remain out of scope and require separate authorization.

## 3. Establish a reproducible baseline

Local execution and existing checks were explicitly authorized. The baseline
passed using existing dependencies. Offline SQLite API tests and rendered
Alembic SQL are used for the feature; PostgreSQL tests still require an
authorized disposable database. Record actual results and blockers rather than
treating existing build artifacts or caches as evidence that checks passed.

## 4. Deliver a narrow vertical slice

Implement the private per-account request workflow in the existing app directories.
Use focused tests, a read-only review of the fixed change set, and explicit stop
conditions. Record verified outcomes in `../SPRINT.md`; update `CREDIT-LOG.md`
only if reliable authorized usage measurements are available. Add no tool or
script unless repeated work demonstrates its value.

## 5. Review and demonstrate

Perform a scoped security review and resolve or disclose findings. Validate the
core workflow, failure cases, setup instructions, and demo with permitted data.
Use the existing release prompt explicitly when preparing the demo/release.
Publication and deployment require separate authorization; a local demo can
remain local. Follow `../SPRINT.md` as a proposed sequence, not proof of completion.
