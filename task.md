Proposal Separation Tasks

Design
- Confirm proposal ownership rules (admin, client, agent access) and expected list/detail behaviors.
- Decide on proposal status transitions (use `ProposalState` or expand).

Schema and Data Layer
- Add `schemas/proposals.py` with `JobProposalBase/Create/Update/Out` models.
- Add `repositories/proposals.py` with CRUD helpers and list filters by `job_id` and `agent_id`.
- Add `services/proposals_service.py` with validation and access checks.

API Layer
- Add `api/v1/proposals.py` with list/detail endpoints for job, agent, client, admin.
- Register proposal routes in `main.py`.
- Update `api/v1/jobs.py` proposal endpoints to create proposal docs and keep legacy fields in sync.

Compatibility and Migration
- Add `latest_proposal_id` to `schemas/jobs.py` outputs and updates (optional).
- Keep legacy proposal fields on jobs while dual-writing for compatibility.
- Add a backfill script under `scripts/` to create proposal docs from existing jobs.

Tests and Docs
- Update/add tests in `tests/` for proposal creation and retrieval endpoints.
- Document new endpoints and deprecations in `readme.md` (or API docs section).

Rollout
- Run backfill in staging.
- Monitor new proposal endpoints and job endpoint responses for correctness.
- Plan deprecation timeline for legacy job proposal fields.
