from fastapi import HTTPException
from fastapi.testclient import TestClient
from limits.storage import MemoryStorage
from limits.strategies import FixedWindowRateLimiter

import main
from api.v1 import jobs as jobs_router
from schemas.agent import AgentOut
from schemas.imports import (
    AvailableHoursAgentCanCommit,
    JobCatgeries,
    JobTimeline,
    UTCOffsets,
)
from schemas.jobs import JobsOut, JobsUpdate
from security.auth import verify_admin_token, verify_client_token


class DummyCelery:
    def send_task(self, *args, **kwargs):
        return "task-id"


def _sample_agent(agent_id: str) -> AgentOut:
    return AgentOut(
        _id=agent_id,
        email="agent@example.com",
        password="hashed",
        full_name="Test Agent",
        phone_number="+2348012345678",
        certificate_url=["https://example.com/cert.pdf"],
        video_url="https://example.com/video.mp4",
        personality_url="https://example.com/personality.pdf",
        primary_area_of_expertise=JobCatgeries.web_development,
        years_of_experience=5,
        three_most_commonly_used_tools_or_platforms=["Figma"],
        available_hours_agent_can_commit=AvailableHoursAgentCanCommit.twenty,
        time_zone=UTCOffsets.UTC_PLUS_01_00,
        portfolio_link="https://portfolio.example.com",
        is_agent_open_to_calls_and_video_meetings=True,
        does_agent_have_working_computer=True,
        does_agent_have_stable_internet=True,
        is_agent_comfortable_with_time_tracking_tools=True,
        date_created=1700000000,
        last_updated=1700000000,
    )


def _sample_job(job_id: str) -> JobsOut:
    return JobsOut(
        _id=job_id,
        project_title="Test Job",
        primary_area_of_expertise=JobCatgeries.web_development,
        description="Build a demo",
        timeline=JobTimeline(start_date=1700000000),
        client_id="client-123",
        admin_approved=False,
        client_approved=False,
        selected_agents=[],
        proposal=None,
    )


def _client():
    main.storage = MemoryStorage()
    main.limiter = FixedWindowRateLimiter(main.storage)
    return TestClient(main.app)


def test_admin_can_submit_proposal(monkeypatch):
    agent = _sample_agent("67514f4bf011bc33ab3c25e9")
    job = _sample_job("64a7f91e92d8b3aef1234567")

    async def fake_retrieve(job_id: str):
        return job

    async def fake_update(job_id: str, jobs_data: JobsUpdate):
        updated = job.model_copy(update=jobs_data.model_dump(exclude_none=True))
        return updated

    async def fake_retrieve_agent(agent_id: str):
        return agent

    monkeypatch.setattr(jobs_router, "retrieve_jobs_by_jobs_id", fake_retrieve)
    monkeypatch.setattr(jobs_router, "update_jobs_by_id", fake_update)
    monkeypatch.setattr(jobs_router, "celery_app", DummyCelery())
    monkeypatch.setattr(
        "services.jobs_service.retrieve_agent_by_agent_id", fake_retrieve_agent
    )

    def override_admin():
        return {"userId": "admin-1", "role": "admin"}

    main.app.dependency_overrides[verify_admin_token] = override_admin

    with _client() as client:
        response = client.post(
            "/v1/jobss/propose/64a7f91e92d8b3aef1234567",
            json={
                "agent_id": agent.id,
                "proposal": "We can deliver in 2 weeks.",
                "break_down": {"Charges": 7, "Tax": 10},
                "timeline": {"start_date": 1700001000},
            },
        )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["proposal"] == "We can deliver in 2 weeks."
    assert data["proposal_created_by_role"] == "admin"
    assert data["proposal_agent_id"] == agent.id
    assert "budget" not in data

    main.app.dependency_overrides.clear()


def test_non_admin_cannot_submit_proposal(monkeypatch):
    def override_admin():
        raise HTTPException(status_code=403, detail="Forbidden")

    main.app.dependency_overrides[verify_admin_token] = override_admin
    monkeypatch.setattr(jobs_router, "celery_app", DummyCelery())

    with _client() as client:
        response = client.post(
            "/v1/jobss/propose/64a7f91e92d8b3aef1234567",
            json={
                "agent_id": "67514f4bf011bc33ab3c25e9",
                "proposal": "Nope",
            },
        )

    assert response.status_code == 403
    main.app.dependency_overrides.clear()


def test_budget_is_rejected_on_job_create(monkeypatch):
    def override_client():
        class Token:
            userId = "client-123"

        return Token()

    main.app.dependency_overrides[verify_client_token] = override_client
    monkeypatch.setattr(jobs_router, "celery_app", DummyCelery())

    with _client() as client:
        response = client.post(
            "/v1/jobss/",
            json={
                "project_title": "Demo",
                "primary_area_of_expertise": "Web Development",
                "budget": 2500,
                "description": "Test",
                "timeline": {"start_date": 1700000000},
            },
        )

    assert response.status_code == 422
    main.app.dependency_overrides.clear()
