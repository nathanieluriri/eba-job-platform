Proposal Separation Plan

Goal
- Move job proposals into their own collection tied to agents so proposals can be retrieved independently of job records.
- Preserve current job endpoints and response shapes during transition to avoid breaking clients.

Current State
- Proposals are embedded on job documents via `proposal`, `proposal_created_by_*`, `proposal_agent_id`, and `selected_agents` in `schemas/jobs.py`.
- Admin proposal flow is handled by `POST /v1/jobss/propose/{job_id}` and stored on the job itself.

Proposed Data Model
- New collection: `job_proposals` (MongoDB).
- New schema module: `schemas/proposals.py` with Pydantic models:
  - `JobProposalBase`: `job_id`, `agent_id`, `proposal`, `break_down`, `timeline`, `status` (use `ProposalState`), `created_by_user_id`, `created_by_role`, `created_via`, `date_created`, `last_updated`.
  - `JobProposalCreate` and `JobProposalUpdate` following the `*Base`, `*Create`, `*Update`, `*Out` pattern.
  - `JobProposalOut` with `id` field mapping `_id`.

API and Service Changes
- New routes module: `api/v1/proposals.py` with endpoints:
  - `GET /v1/proposals/job/{job_id}` (admin/client/agent depending on role) to list proposals for a job.
  - `GET /v1/proposals/agent/` for agents to list their proposals (filter by agent_id from token).
  - `GET /v1/proposals/client/` for clients to list proposals for their jobs (join via job_id).
  - `GET /v1/proposals/{proposal_id}` for detail view (role-based access).
- New repository/service modules: `repositories/proposals.py` and `services/proposals_service.py` patterned after jobs/logs.
- Update `POST /v1/jobss/propose/{job_id}` to:
  - Create a proposal document in `job_proposals`.
  - Update the job with `selected_agents` and legacy proposal fields for backward compatibility.
- Update `GET /v1/jobss/*` responses to optionally include a `latest_proposal_id` (new field) while still returning legacy proposal fields.

Compatibility Strategy
- Dual-write during transition: proposals are written to `job_proposals` and the latest proposal is denormalized onto the job.
- Dual-read during transition: existing clients read job fields; new consumers can query proposals endpoints.
- Mark legacy fields (`proposal`, `proposal_created_by_*`, `proposal_agent_id`) as deprecated in docs but keep them populated until client migration is complete.

Migration / Backfill
- Add a one-off script (e.g., `scripts/backfill_job_proposals.py`) to scan jobs where `proposal` exists and insert proposal documents.
- Record the new proposal IDs on the job (`latest_proposal_id`) and keep existing fields intact.

Rollout Plan
1) Add new schemas, repository, service, and API routes for proposals.
2) Update admin proposal flow to create proposal docs and keep legacy fields in sync.
3) Backfill existing proposals from job documents.
4) Update documentation and notify clients to switch to proposal endpoints.
5) After adoption, consider removing legacy fields or leaving them read-only.

Risks and Notes
- Be careful with permissions: proposals should be visible only to the owning client/admin/agent.
- Avoid changing existing response shapes without explicit versioning.
- Consider indexes on `job_id` and `agent_id` in `job_proposals` for fast lookups.
