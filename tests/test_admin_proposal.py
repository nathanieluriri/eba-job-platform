from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import httpx
import pytest
from dotenv import load_dotenv


Role = str


@dataclass
class Ctx:
    base_url: str
    allow_stateful: bool
    ids: Dict[str, str]


def _env(key: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(key)
    if value is None:
        return default
    value = value.strip()
    return value if value else default


def _bool_env(key: str, default: bool = False) -> bool:
    value = (_env(key) or "").lower()
    if value in ("1", "true", "yes", "y", "on"):
        return True
    if value in ("0", "false", "no", "n", "off"):
        return False
    return default


def _unwrap_data(resp_json: Dict[str, object]) -> Dict[str, object]:
    return resp_json.get("data") or {}


def _unique_email(prefix: str) -> str:
    return f"{prefix}.{uuid.uuid4().hex[:10]}@example.com"


def _login_payload(email: str, password: str) -> Dict[str, str]:
    return {"email": email, "password": password}


def _admin_creds() -> Tuple[Optional[str], Optional[str]]:
    email = "superadmin@gmail.com"
    password = "string"
    return email, password


def _request(client: httpx.Client, method: str, url: str, *, params=None, json_body=None, headers=None) -> httpx.Response:
    return client.request(method, url, params=params, json=json_body, headers=headers)


def _auth_header(token: Optional[str]) -> Dict[str, str]:
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def _admin_headers(admin_access: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {admin_access}"}


def _admin_login(client: httpx.Client, base_url: str, email: str, password: str) -> Tuple[Optional[str], Optional[str]]:
    resp = client.post(f"{base_url}/v1/admins/login", json=_login_payload(email, password))
    if resp.status_code != 200:
        _log(f"Admin login failed: {resp.status_code} {resp.text}")
        return None, None
    data = _unwrap_data(resp.json())
    return data.get("access_token"), data.get("refresh_token")


def _login(client: httpx.Client, base_url: str, role: str, email: str, password: str) -> Tuple[Optional[str], Optional[str]]:
    resp = client.post(f"{base_url}/v1/{role}s/login", json=_login_payload(email, password))
    if resp.status_code != 200:
        _log(f"{role} login failed: {resp.status_code} {resp.text}")
        return None, None
    data = _unwrap_data(resp.json())
    return data.get("access_token"), data.get("refresh_token")


def _base_user_payload(role: str, email: str, password: str) -> Dict[str, object]:
    base: Dict[str, object] = {
        "email": email,
        "password": password,
        "full_name": f"{role.title()} User",
        "phone_number": "+1234567890",
        "certificate_url": ["https://example.com/cert.pdf"],
        "video_url": "https://example.com/intro.mp4",
        "personality_url": "https://example.com/personality.pdf",
    }
    if role == "client":
        base.update(
            {
                "role": "client",
                "company_name": "Test Co",
                "company_email": email,
                "company_address": "123 Test Street",
                "client_reason_for_signing_up": "Test account",
                "client_need_agent_work_hours_to_be": "both",
            }
        )
    else:
        base.update(
            {
                "role": "agent",
                "primary_area_of_expertise": "Web Development",
                "years_of_experience": 3,
                "three_most_commonly_used_tools_or_platforms": ["Jira", "Slack"],
                "available_hours_agent_can_commit": 80,
                "time_zone": "UTC+01:00",
                "portfolio_link": "https://portfolio.example.com",
                "is_agent_open_to_calls_and_video_meetings": True,
                "does_agent_have_working_computer": True,
                "does_agent_have_stable_internet": True,
                "is_agent_comfortable_with_time_tracking_tools": True,
            }
        )
    return base


def _find_user_id_by_email(client: httpx.Client, base_url: str, admin_access: str, email: str) -> Optional[str]:
    resp = client.get(f"{base_url}/v1/users/", headers=_admin_headers(admin_access), params={"start": 0, "stop": 100})
    if resp.status_code != 200:
        return None
    for item in (_unwrap_data(resp.json()) or []):
        if str(item.get("email", "")).lower() == email.lower():
            return item.get("id")
    return None


def _approve_user(client: httpx.Client, base_url: str, admin_access: str, user_id: str) -> bool:
    resp = client.patch(f"{base_url}/v1/users/{user_id}/approve", headers=_admin_headers(admin_access))
    return resp.status_code == 200


def _create_and_approve_user(
    client: httpx.Client,
    base_url: str,
    admin_access: str,
    role: str,
    email: str,
    password: str,
) -> bool:
    payload = _base_user_payload(role=role, email=email, password=password)
    resp = client.post(f"{base_url}/v1/users/signup", json=payload)
    if resp.status_code not in (200, 409, 422):
        _log(f"{role} signup failed: {resp.status_code} {resp.text}")
        return False
    if resp.status_code == 422:
        _log(f"{role} signup validation failed: {resp.text}")

    user_id = _find_user_id_by_email(client, base_url, admin_access, email)
    if not user_id:
        _log(f"{role} approval lookup failed for {email}")
        return False

    approved = _approve_user(client, base_url, admin_access, user_id)
    if not approved:
        _log(f"{role} approval failed for {user_id}")
    return approved


def _extract_id(resp: httpx.Response) -> Optional[str]:
    try:
        data = _unwrap_data(resp.json())
    except Exception:
        return None
    if isinstance(data, dict):
        return data.get("id")
    return None


def _get_agent_id(client: httpx.Client, base_url: str, token: str) -> Optional[str]:
    resp = client.get(f"{base_url}/v1/agents/me", headers=_auth_header(token))
    return _extract_id(resp)


def _get_client_id(client: httpx.Client, base_url: str, token: str) -> Optional[str]:
    resp = client.get(f"{base_url}/v1/clients/me", headers=_auth_header(token))
    return _extract_id(resp)


def _create_job(client: httpx.Client, base_url: str, token: str, title: str) -> Optional[str]:
    payload = {
        "project_title": title,
        "primary_area_of_expertise": "Web Development",
        "description": "Proposal flow integration test",
        "timeline": {"start_date": int(time.time())},
    }
    resp = client.post(f"{base_url}/v1/jobss/", json=payload, headers=_auth_header(token))
    if resp.status_code != 200:
        return None
    return None


def _find_job_id(client: httpx.Client, base_url: str, token: str, title: str) -> Optional[str]:
    resp = client.get(
        f"{base_url}/v1/jobss/client/created/",
        headers=_auth_header(token),
        params={"start": 0, "stop": 50},
    )
    if resp.status_code != 200:
        return None
    for item in (_unwrap_data(resp.json()) or []):
        if item.get("project_title") == title:
            return item.get("id")
    return None


def _save_user_tokens(path: str, payload: Dict[str, object]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def _load_state(path: str) -> Dict[str, str]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict):
            return {k: str(v) for k, v in data.items()}
    except Exception:
        return {}
    return {}


def _save_state(path: str, payload: Dict[str, str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def _log(msg: str) -> None:
    os.makedirs("reports", exist_ok=True)
    with open("reports/test_admin_proposal.log", "a", encoding="utf-8") as handle:
        handle.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")


@pytest.fixture(scope="session")
def ctx() -> Ctx:
    load_dotenv()
    base_url = (_env("BASE_URL") or "https://eba.3nis.net").rstrip("/")
    allow_stateful = _bool_env("ALLOW_STATEFUL", default=True)
    ids = _load_state("reports/test_ids.json")
    return Ctx(base_url=base_url, allow_stateful=allow_stateful, ids=ids)


@pytest.fixture(scope="session")
def client() -> httpx.Client:
    return httpx.Client(timeout=30.0, follow_redirects=True)


@pytest.fixture(scope="session")
def tokens(client: httpx.Client, ctx: Ctx) -> Dict[str, Dict[str, Optional[str]]]:
    admin_email, admin_password = _admin_creds()
    if not admin_email or not admin_password:
        _log("Admin credentials missing (ADMIN_EMAIL/ADMIN_PASSWORD).")
        pytest.fail("Admin credentials missing (ADMIN_EMAIL/ADMIN_PASSWORD)")

    admin_access, admin_refresh = _admin_login(client, ctx.base_url, admin_email, admin_password)
    if not admin_access:
        _log("Admin login failed; cannot run proposal flow.")
        pytest.fail("Admin login failed; cannot run proposal flow")

    client_email = _env("CLIENT_EMAIL") or _unique_email("client")
    client_password = _env("CLIENT_PASSWORD") or "ClientPass123!"
    client_access, client_refresh = _login(client, ctx.base_url, "client", client_email, client_password)
    if not client_access:
        ok = _create_and_approve_user(client, ctx.base_url, admin_access, "client", client_email, client_password)
        if ok:
            for _ in range(3):
                time.sleep(0.5)
                client_access, client_refresh = _login(client, ctx.base_url, "client", client_email, client_password)
                if client_access:
                    break

    agent_email = _env("AGENT_EMAIL") or _unique_email("agent")
    agent_password = _env("AGENT_PASSWORD") or "AgentPass123!"
    agent_access, agent_refresh = _login(client, ctx.base_url, "agent", agent_email, agent_password)
    if not agent_access:
        ok = _create_and_approve_user(client, ctx.base_url, admin_access, "agent", agent_email, agent_password)
        if ok:
            for _ in range(3):
                time.sleep(0.5)
                agent_access, agent_refresh = _login(client, ctx.base_url, "agent", agent_email, agent_password)
                if agent_access:
                    break

    if not client_access or not agent_access:
        _log("Client/Agent login failed; cannot run proposal flow.")
        pytest.fail("Client/Agent login failed; cannot run proposal flow")

    _save_user_tokens(
        "reports/auth_users.json",
        {
            "client": {
                "email": client_email,
                "password": client_password,
                "access_token": client_access,
                "refresh_token": client_refresh,
            },
            "agent": {
                "email": agent_email,
                "password": agent_password,
                "access_token": agent_access,
                "refresh_token": agent_refresh,
            },
        },
    )

    return {
        "admin": {"access": admin_access, "refresh": admin_refresh},
        "client": {"access": client_access, "refresh": client_refresh},
        "agent": {"access": agent_access, "refresh": agent_refresh},
    }


def _ensure_job_id(client: httpx.Client, ctx: Ctx, tokens: Dict[str, Dict[str, Optional[str]]]) -> Optional[str]:
    if ctx.ids.get("JOB_ID"):
        return ctx.ids["JOB_ID"]
    if not ctx.allow_stateful:
        return None

    title = f"Proposal Test Job {uuid.uuid4().hex[:6]}"
    _create_job(client, ctx.base_url, tokens["client"]["access"], title)
    for _ in range(10):
        time.sleep(1)
        job_id = _find_job_id(client, ctx.base_url, tokens["client"]["access"], title)
        if job_id:
            ctx.ids["JOB_ID"] = job_id
            _save_state("reports/test_ids.json", ctx.ids)
            return job_id
    return None


def _ensure_agent_id(client: httpx.Client, ctx: Ctx, tokens: Dict[str, Dict[str, Optional[str]]]) -> Optional[str]:
    if ctx.ids.get("AGENT_ID"):
        return ctx.ids["AGENT_ID"]
    agent_id = _get_agent_id(client, ctx.base_url, tokens["agent"]["access"])
    if agent_id:
        ctx.ids["AGENT_ID"] = agent_id
        _save_state("reports/test_ids.json", ctx.ids)
    return agent_id


def _ensure_client_id(client: httpx.Client, ctx: Ctx, tokens: Dict[str, Dict[str, Optional[str]]]) -> Optional[str]:
    if ctx.ids.get("CLIENT_ID"):
        return ctx.ids["CLIENT_ID"]
    client_id = _get_client_id(client, ctx.base_url, tokens["client"]["access"])
    if client_id:
        ctx.ids["CLIENT_ID"] = client_id
        _save_state("reports/test_ids.json", ctx.ids)
    return client_id


def _submit_proposal(
    client: httpx.Client,
    ctx: Ctx,
    admin_token: str,
    job_id: str,
    agent_id: str,
    proposal_text: str,
) -> str:
    payload = {
        "agent_id": agent_id,
        "proposal": proposal_text,
        "break_down": {"Charges": 7, "Tax": 10},
        "timeline": {"start_date": int(time.time())},
    }
    propose_url = f"{ctx.base_url}/v1/jobss/propose/{job_id}"
    resp = _request(client, "POST", propose_url, json_body=payload, headers=_auth_header(admin_token))
    assert resp.status_code == 200, resp.text
    data = _unwrap_data(resp.json())
    proposal_id = data.get("latest_proposal_id")
    assert proposal_id, "latest_proposal_id missing from proposal response"
    return proposal_id


def _fetch_proposal_admin(client: httpx.Client, ctx: Ctx, admin_token: str, proposal_id: str) -> Dict[str, object]:
    resp = _request(
        client,
        "GET",
        f"{ctx.base_url}/v1/proposals/admin/{proposal_id}",
        headers=_auth_header(admin_token),
    )
    assert resp.status_code == 200, resp.text
    return _unwrap_data(resp.json())


def _accept_proposal(client: httpx.Client, ctx: Ctx, client_token: str, job_id: str) -> None:
    resp = _request(
        client,
        "PATCH",
        f"{ctx.base_url}/v1/jobss/client/accept-proposal/{job_id}",
        json_body={"client_approved": True},
        headers=_auth_header(client_token),
    )
    assert resp.status_code == 200, resp.text


def _reject_proposal(client: httpx.Client, ctx: Ctx, client_token: str, job_id: str) -> None:
    resp = _request(
        client,
        "PATCH",
        f"{ctx.base_url}/v1/jobss/client/reject-proposal/{job_id}",
        json_body={"client_approved": False, "client_rejection_reason": "Integration test rejection"},
        headers=_auth_header(client_token),
    )
    assert resp.status_code == 200, resp.text


def test_proposal_flow(client: httpx.Client, ctx: Ctx, tokens: Dict[str, Dict[str, Optional[str]]]):
    agent_id = _ensure_agent_id(client, ctx, tokens)
    client_id = _ensure_client_id(client, ctx, tokens)

    if not agent_id:
        _log("Agent ID missing; cannot submit proposal.")
        pytest.fail("Agent ID missing; cannot submit proposal")
    if not client_id:
        _log("Client ID missing; cannot validate client access.")
        pytest.fail("Client ID missing; cannot validate client access")

    job_id_accept = _ensure_job_id(client, ctx, tokens)
    assert job_id_accept, "JOB_ID missing and job creation did not yield a job to test against"

    job_id_reject = ctx.ids.get("JOB_ID_REJECT")
    if not job_id_reject:
        title = f"Proposal Reject Job {uuid.uuid4().hex[:6]}"
        _create_job(client, ctx.base_url, tokens["client"]["access"], title)
        for _ in range(10):
            time.sleep(1)
            job_id_reject = _find_job_id(client, ctx.base_url, tokens["client"]["access"], title)
            if job_id_reject:
                ctx.ids["JOB_ID_REJECT"] = job_id_reject
                _save_state("reports/test_ids.json", ctx.ids)
                break
    assert job_id_reject, "JOB_ID_REJECT missing and job creation did not yield a job to test against"

    proposal_id_accept = _submit_proposal(
        client,
        ctx,
        tokens["admin"]["access"],
        job_id_accept,
        agent_id,
        "Integration test proposal payload (accept).",
    )

    proposal_id_reject = _submit_proposal(
        client,
        ctx,
        tokens["admin"]["access"],
        job_id_reject,
        agent_id,
        "Integration test proposal payload (reject).",
    )

    list_admin = _request(
        client,
        "GET",
        f"{ctx.base_url}/v1/proposals/admin/job/{job_id_accept}",
        headers=_auth_header(tokens["admin"]["access"]),
    )
    assert list_admin.status_code == 200, list_admin.text
    admin_list = _unwrap_data(list_admin.json())
    assert any(item.get("id") == proposal_id_accept for item in admin_list), "proposal not found in admin list"

    list_agent = _request(
        client,
        "GET",
        f"{ctx.base_url}/v1/proposals/agent/",
        params={"start": 0, "stop": 50},
        headers=_auth_header(tokens["agent"]["access"]),
    )
    assert list_agent.status_code == 200, list_agent.text

    list_client = _request(
        client,
        "GET",
        f"{ctx.base_url}/v1/proposals/client/",
        params={"start": 0, "stop": 50},
        headers=_auth_header(tokens["client"]["access"]),
    )
    assert list_client.status_code == 200, list_client.text

    detail_accept = _fetch_proposal_admin(client, ctx, tokens["admin"]["access"], proposal_id_accept)
    assert detail_accept.get("job_id") == job_id_accept
    assert detail_accept.get("agent_id") == agent_id

    detail_reject = _fetch_proposal_admin(client, ctx, tokens["admin"]["access"], proposal_id_reject)
    assert detail_reject.get("job_id") == job_id_reject
    assert detail_reject.get("agent_id") == agent_id

    _accept_proposal(client, ctx, tokens["client"]["access"], job_id_accept)
    _reject_proposal(client, ctx, tokens["client"]["access"], job_id_reject)

    updated_accept = _fetch_proposal_admin(client, ctx, tokens["admin"]["access"], proposal_id_accept)
    updated_reject = _fetch_proposal_admin(client, ctx, tokens["admin"]["access"], proposal_id_reject)

    assert updated_accept.get("status") == "accepted"
    assert updated_reject.get("status") == "rejected"
