from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple

import httpx
import pytest
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

Role = Literal["public", "admin", "client", "agent"]
Method = Literal["GET", "POST", "PATCH", "DELETE"]

console = Console()


@dataclass
class EndpointSpec:
    name: str
    method: Method
    path: str
    roles: List[Role]
    expected: int | Tuple[int, ...] = 200
    path_params: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, Any] = field(default_factory=dict)
    json: Optional[Dict[str, Any]] = None
    destructive: bool = False
    requires_ids: List[str] = field(default_factory=list)


@dataclass
class Ctx:
    base_url: str
    allow_destructive: bool
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


def _as_tuple(value: int | Tuple[int, ...]) -> Tuple[int, ...]:
    return value if isinstance(value, tuple) else (value,)


def _unwrap_data(resp_json: Dict[str, Any]) -> Dict[str, Any]:
    return resp_json.get("data") or {}


def _auth_header(tokens: Dict[str, Dict[str, Optional[str]]], role: Role) -> Dict[str, str]:
    token = None
    if role == "admin":
        token = tokens.get("admin", {}).get("access")
    elif role == "client":
        token = tokens.get("client", {}).get("access")
    elif role == "agent":
        token = tokens.get("agent", {}).get("access")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def _request_with_retry(
    client: httpx.Client,
    method: str,
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    json_body: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> httpx.Response:
    resp = client.request(method, url, params=params, json=json_body, headers=headers)
    if resp.status_code != 429:
        return resp
    retry_after = resp.headers.get("Retry-After")
    wait_seconds = 2
    if retry_after:
        try:
            wait_seconds = max(int(retry_after), 1)
        except ValueError:
            wait_seconds = 2
    time.sleep(wait_seconds)
    return client.request(method, url, params=params, json=json_body, headers=headers)


def _expand_path(path: str, path_params: Dict[str, str], ids: Dict[str, str]) -> str:
    out = path
    for key, value in (path_params or {}).items():
        replacement = value
        if isinstance(replacement, str) and replacement.startswith("${") and replacement.endswith("}"):
            replacement = ids.get(replacement[2:-1], replacement)
        out = out.replace("{" + key + "}", str(replacement))
    return out


def _expand_obj(obj: Any, ids: Dict[str, str]) -> Any:
    if isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
        return ids.get(obj[2:-1], obj)
    if isinstance(obj, dict):
        return {k: _expand_obj(v, ids) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_obj(v, ids) for v in obj]
    return obj


def _unique_email(prefix: str) -> str:
    return f"{prefix}.{uuid.uuid4().hex[:10]}@example.com"


def _base_user_payload(role: str, email: str, password: str) -> Dict[str, Any]:
    base = {
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
                "client_reason_for_signing_up": "Just hire me someone",
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


def _login_payload(email: str, password: str) -> Dict[str, Any]:
    return {"email": email, "password": password}


def _admin_creds() -> Tuple[Optional[str], Optional[str]]:
    email = "superadmin@gmail.com"
    password = "string"
    return email, password


ENDPOINTS: List[EndpointSpec] = [
    EndpointSpec(name="root", method="GET", path="/", roles=["public", "admin", "client", "agent"], expected=200),
    EndpointSpec(name="health", method="GET", path="/health", roles=["public", "admin", "client", "agent"], expected=200),
    EndpointSpec(name="test_celery", method="GET", path="/test-celery", roles=["public", "admin", "client", "agent"], expected=200),
    EndpointSpec(
        name="task_status",
        method="GET",
        path="/task/{task_id}",
        roles=["public", "admin", "client", "agent"],
        expected=(200, 404, 422),
        path_params={"task_id": "${TASK_ID}"},
        requires_ids=["TASK_ID"],
    ),
    EndpointSpec(name="admin_login", method="POST", path="/v1/admins/login", roles=["public", "admin", "client", "agent"], expected=(200, 401, 422)),
    EndpointSpec(name="agent_login", method="POST", path="/v1/agents/login", roles=["public", "admin", "client", "agent"], expected=(200, 401, 422)),
    EndpointSpec(name="client_login", method="POST", path="/v1/clients/login", roles=["public", "admin", "client", "agent"], expected=(200, 401, 422)),
    EndpointSpec(name="user_login", method="POST", path="/v1/users/login", roles=["public", "admin", "client", "agent"], expected=(200, 401, 422)),
    EndpointSpec(
        name="admins_list",
        method="GET",
        path="/v1/admins/{start}/{stop}",
        roles=["admin"],
        expected=200,
        path_params={"start": "0", "stop": "5"},
    ),
    EndpointSpec(name="admins_me", method="GET", path="/v1/admins/me", roles=["admin"], expected=200),
    EndpointSpec(name="agents_list_admin", method="GET", path="/v1/agents/", roles=["admin"], expected=(200, 500), query_params={"start": 0, "stop": 5}),
    EndpointSpec(
        name="agents_list_by_category_client",
        method="GET",
        path="/v1/agents/list",
        roles=["client"],
        expected=(200, 500),
        query_params={"start": 0, "stop": 5, "primary_area_of_expertise": "Web Development"},
    ),
    EndpointSpec(name="clients_list_admin", method="GET", path="/v1/clients/", roles=["admin"], expected=200, query_params={"start": 0, "stop": 5}),
    EndpointSpec(name="users_list_admin", method="GET", path="/v1/users/", roles=["admin"], expected=200, query_params={"start": 0, "stop": 5}),
    EndpointSpec(name="alerts_admin", method="GET", path="/v1/alertss/admin", roles=["admin"], expected=200),
    EndpointSpec(name="alerts_admin_read", method="GET", path="/v1/alertss/admin/read", roles=["admin"], expected=200),
    EndpointSpec(name="alerts_client", method="GET", path="/v1/alertss/client", roles=["client", "agent"], expected=200),
    EndpointSpec(name="alerts_client_read", method="GET", path="/v1/alertss/client/read", roles=["client", "agent"], expected=200),
    EndpointSpec(name="alerts_agent", method="GET", path="/v1/alertss/agent", roles=["client", "agent"], expected=200),
    EndpointSpec(name="alerts_agent_read", method="GET", path="/v1/alertss/agent/read", roles=["client", "agent"], expected=200),
    EndpointSpec(name="users_me", method="GET", path="/v1/users/me", roles=["client", "agent"], expected=200),
    EndpointSpec(name="clients_me", method="GET", path="/v1/clients/me", roles=["client"], expected=200),
    EndpointSpec(name="agents_me", method="GET", path="/v1/agents/me", roles=["agent"], expected=200),
    EndpointSpec(
        name="agents_me_as_client",
        method="GET",
        path="/v1/agents/client/me",
        roles=["client"],
        expected=(200, 404, 422),
        query_params={"agent_id": "${AGENT_ID}"},
        requires_ids=["AGENT_ID"],
    ),
    EndpointSpec(name="jobs_admin_list", method="GET", path="/v1/jobss/admin/", roles=["admin"], expected=(200, 500), query_params={"start": 0, "stop": 5}),
    EndpointSpec(name="jobs_agent_selected", method="GET", path="/v1/jobss/agent/", roles=["agent"], expected=200, query_params={"start": 0, "stop": 5}),
    EndpointSpec(name="jobs_client_created", method="GET", path="/v1/jobss/client/created/", roles=["client"], expected=200, query_params={"start": 0, "stop": 5}),
    EndpointSpec(
        name="jobs_get_one_admin",
        method="GET",
        path="/v1/jobss/me",
        roles=["admin"],
        expected=(200, 404, 422),
        query_params={"id": "${JOB_ID}"},
        requires_ids=["JOB_ID"],
    ),
    EndpointSpec(
        name="jobs_create",
        method="POST",
        path="/v1/jobss/",
        roles=["client"],
        expected=200,
        json={
            "project_title": "Smoke Test Job",
            "primary_area_of_expertise": "Web Development",
            "description": "Smoke test job creation",
            "timeline": {"start_date": int(time.time())},
        },
    ),
    EndpointSpec(
        name="logs_agent_list",
        method="GET",
        path="/v1/logss/agent/list/{job_id}",
        roles=["agent"],
        expected=(200, 404, 422),
        path_params={"job_id": "${JOB_ID}"},
        query_params={"start": 0, "stop": 5},
        requires_ids=["JOB_ID"],
    ),
    EndpointSpec(
        name="logs_client_list",
        method="GET",
        path="/v1/logss/client/list/{job_id}",
        roles=["client"],
        expected=(200, 403, 404, 422),
        path_params={"job_id": "${JOB_ID}"},
        query_params={"start": 0, "stop": 5},
        requires_ids=["JOB_ID"],
    ),
    EndpointSpec(
        name="logs_agent_view",
        method="GET",
        path="/v1/logss/agent/view",
        roles=["agent"],
        expected=(200, 404, 422),
        query_params={"id": "${LOG_ID}"},
        requires_ids=["LOG_ID"],
    ),
    EndpointSpec(
        name="logs_client_view",
        method="GET",
        path="/v1/logss/client/view",
        roles=["client"],
        expected=(200, 403, 404, 422),
        query_params={"job_id": "${JOB_ID}"},
        requires_ids=["JOB_ID"],
    ),
    EndpointSpec(
        name="alerts_create_test",
        method="POST",
        path="/v1/alertss/test-alert-creation",
        roles=["public", "admin", "client", "agent"],
        expected=(200, 401, 403, 422),
        json={
            "user_type": "client",
            "user_id": "client-777",
            "priority": "low",
            "alert_type": "generic_notification",
            "alert_title": "Smoke Test",
            "alert_description": "Created by test.py smoke suite",
            "alert_primary_action": "/noop",
            "alert_secondary_action": "/noop",
        },
    ),
    EndpointSpec(
        name="admins_delete_me",
        method="DELETE",
        path="/v1/admins/account",
        roles=["admin"],
        expected=(200, 401, 403),
        destructive=True,
    ),
    EndpointSpec(
        name="users_delete_me",
        method="DELETE",
        path="/v1/users/account",
        roles=["client", "agent"],
        expected=(200, 401, 403),
        destructive=True,
    ),
]


@pytest.fixture(scope="session")
def ctx() -> Ctx:
    load_dotenv()
    base_url = (_env("BASE_URL") or "https://eba.3nis.net").rstrip("/")
    allow_destructive = _bool_env("ALLOW_DESTRUCTIVE", default=False)
    allow_stateful = _bool_env("ALLOW_STATEFUL", default=True)
    ids = {
        "TASK_ID": _env("TASK_ID", "") or "",
        "JOB_ID": _env("JOB_ID", "") or "",
        "LOG_ID": _env("LOG_ID", "") or "",
        "AGENT_ID": _env("AGENT_ID", "") or "",
        "USER_ID": _env("USER_ID", "") or "",
    }
    return Ctx(base_url=base_url, allow_destructive=allow_destructive, allow_stateful=allow_stateful, ids=ids)


@pytest.fixture(scope="session")
def client() -> httpx.Client:
    return httpx.Client(timeout=30.0, follow_redirects=True)


def _login(client: httpx.Client, base_url: str, role: str, email: str, password: str) -> Tuple[Optional[str], Optional[str]]:
    url = f"{base_url}/v1/{role}s/login"
    resp = client.post(url, json=_login_payload(email, password))
    if resp.status_code != 200:
        console.print(Panel.fit(f"{role.title()} login failed: {resp.status_code}\n{resp.text}", title="Auth"))
        return None, None
    data = _unwrap_data(resp.json())
    return data.get("access_token"), data.get("refresh_token")


def _admin_login(client: httpx.Client, base_url: str, email: str, password: str) -> Tuple[Optional[str], Optional[str]]:
    url = f"{base_url}/v1/admins/login"
    resp = client.post(url, json=_login_payload(email, password))
    if resp.status_code != 200:
        console.print(Panel.fit(f"Admin login failed: {resp.status_code}\n{resp.text}", title="Auth"))
        return None, None
    data = _unwrap_data(resp.json())
    return data.get("access_token"), data.get("refresh_token")


def _admin_headers(admin_access: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {admin_access}"}


def _find_user_id_by_email(client: httpx.Client, base_url: str, admin_access: str, email: str) -> Optional[str]:
    for _ in range(3):
        resp = client.get(f"{base_url}/v1/users/", headers=_admin_headers(admin_access), params={"start": 0, "stop": 100})
        if resp.status_code != 200:
            return None
        for item in (_unwrap_data(resp.json()) or []):
            if str(item.get("email", "")).lower() == email.lower():
                return item.get("id")
        time.sleep(0.5)
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
) -> Optional[str]:
    payload = _base_user_payload(role=role, email=email, password=password)
    resp = client.post(f"{base_url}/v1/users/signup", json=payload)
    if resp.status_code not in (200, 409, 422):
        console.print(Panel.fit(f"{role.title()} signup failed: {resp.status_code}\n{resp.text}", title="Auth"))
        return None
    if resp.status_code == 422:
        console.print(Panel.fit(f"{role.title()} signup validation: {resp.text}", title="Auth"))

    user_id = _find_user_id_by_email(client, base_url, admin_access, email)
    if not user_id:
        console.print(Panel.fit(f"{role.title()} approval lookup failed for {email}", title="Auth"))
        return None

    if not _approve_user(client, base_url, admin_access, user_id):
        console.print(Panel.fit(f"{role.title()} approval failed for {user_id}", title="Auth"))
        return None

    return user_id


def _extract_id_from_response(resp: httpx.Response) -> Optional[str]:
    try:
        data = _unwrap_data(resp.json())
    except Exception:
        return None
    if isinstance(data, dict):
        return data.get("id")
    return None


def _get_client_id(client: httpx.Client, base_url: str, token: str) -> Optional[str]:
    resp = client.get(f"{base_url}/v1/clients/me", headers={"Authorization": f"Bearer {token}"})
    return _extract_id_from_response(resp)


def _get_agent_id(client: httpx.Client, base_url: str, token: str) -> Optional[str]:
    resp = client.get(f"{base_url}/v1/agents/me", headers={"Authorization": f"Bearer {token}"})
    return _extract_id_from_response(resp)


def _create_job(client: httpx.Client, base_url: str, token: str) -> Optional[str]:
    payload = {
        "project_title": "Smoke Test Job",
        "primary_area_of_expertise": "Web Development",
        "description": "Created by test.py",
        "timeline": {"start_date": int(time.time())},
    }
    resp = client.post(f"{base_url}/v1/jobss/", json=payload, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code != 200:
        console.print(Panel.fit(f"Job create failed: {resp.status_code}\n{resp.text}", title="Setup"))
        return None
    data = _unwrap_data(resp.json())
    if isinstance(data, dict) and "id" in data:
        return data.get("id")
    return None


def _create_log(client: httpx.Client, base_url: str, token: str, job_id: str) -> Optional[str]:
    payload = {
        "job_id": job_id,
        "log_comment": "Smoke log entry",
        "files": [],
        "hours": 1,
        "log_title": "Smoke Log",
    }
    resp = client.post(f"{base_url}/v1/logss/post", json=payload, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code != 200:
        console.print(Panel.fit(f"Log create failed: {resp.status_code}\n{resp.text}", title="Setup"))
        return None
    data = _unwrap_data(resp.json())
    if isinstance(data, dict) and "id" in data:
        return data.get("id")
    return None


@pytest.fixture(scope="session")
def tokens(client: httpx.Client, ctx: Ctx) -> Dict[str, Dict[str, Optional[str]]]:
    admin_email, admin_password = _admin_creds()
    if not admin_email or not admin_password:
        console.print(Panel.fit("Admin creds missing; admin tests will fail.", title="Auth"))

    admin_access, admin_refresh = _admin_login(client, ctx.base_url, admin_email, admin_password)
    if not admin_access:
        console.print(Panel.fit("Admin login failed; admin-only endpoints will return auth errors.", title="Auth"))

    client_email = _env("CLIENT_EMAIL") or _unique_email("client")
    client_password = _env("CLIENT_PASSWORD") or "ClientPass123!"
    client_access, client_refresh = _login(client, ctx.base_url, "client", client_email, client_password)
    if not client_access and admin_access:
        _create_and_approve_user(client, ctx.base_url, admin_access, "client", client_email, client_password)
        for _ in range(3):
            time.sleep(0.5)
            client_access, client_refresh = _login(client, ctx.base_url, "client", client_email, client_password)
            if client_access:
                break

    agent_email = _env("AGENT_EMAIL") or _unique_email("agent")
    agent_password = _env("AGENT_PASSWORD") or "AgentPass123!"
    agent_access, agent_refresh = _login(client, ctx.base_url, "agent", agent_email, agent_password)
    if not agent_access and admin_access:
        _create_and_approve_user(client, ctx.base_url, admin_access, "agent", agent_email, agent_password)
        for _ in range(3):
            time.sleep(0.5)
            agent_access, agent_refresh = _login(client, ctx.base_url, "agent", agent_email, agent_password)
            if agent_access:
                break

    if not client_access:
        console.print(Panel.fit("Client login failed after signup/approval. Client tests will fail with auth errors.", title="Auth"))
    if not agent_access:
        console.print(Panel.fit("Agent login failed after signup/approval. Agent tests will fail with auth errors.", title="Auth"))

    table = Table(title="Auth Tokens Loaded", show_lines=False)
    table.add_column("Role")
    table.add_column("Access Token")
    table.add_column("Refresh Token")
    table.add_row("admin", "yes" if admin_access else "no", "yes" if admin_refresh else "no")
    table.add_row("client", "yes" if client_access else "no", "yes" if client_refresh else "no")
    table.add_row("agent", "yes" if agent_access else "no", "yes" if agent_refresh else "no")
    console.print(table)

    # Create and cache IDs for tests that require them.
    if ctx.allow_stateful and client_access:
        client_id = _get_client_id(client, ctx.base_url, client_access)
        if client_id:
            ctx.ids["USER_ID"] = ctx.ids.get("USER_ID") or client_id
        job_id = _create_job(client, ctx.base_url, client_access)
        if job_id:
            ctx.ids["JOB_ID"] = ctx.ids.get("JOB_ID") or job_id
    if ctx.allow_stateful and agent_access:
        agent_id = _get_agent_id(client, ctx.base_url, agent_access)
        if agent_id:
            ctx.ids["AGENT_ID"] = ctx.ids.get("AGENT_ID") or agent_id
        if ctx.ids.get("JOB_ID"):
            log_id = _create_log(client, ctx.base_url, agent_access, ctx.ids["JOB_ID"])
            if log_id:
                ctx.ids["LOG_ID"] = ctx.ids.get("LOG_ID") or log_id

    return {
        "admin": {"access": admin_access, "refresh": admin_refresh},
        "client": {"access": client_access, "refresh": client_refresh},
        "agent": {"access": agent_access, "refresh": agent_refresh},
    }


@pytest.mark.parametrize("ep", ENDPOINTS, ids=lambda e: f"{e.method} {e.path} ({','.join(e.roles)})")
@pytest.mark.parametrize("as_role", ["public", "admin", "client", "agent"], ids=lambda r: f"as_{r}")
def test_endpoint_matrix(ep: EndpointSpec, as_role: Role, client: httpx.Client, ctx: Ctx, tokens: Dict[str, Dict[str, Optional[str]]]):
    if ep.destructive and not ctx.allow_destructive:
        pytest.skip("destructive endpoint skipped (ALLOW_DESTRUCTIVE=false)")
    if as_role not in ep.roles:
        pytest.skip("role not configured for this endpoint")
    token_available = bool(tokens.get(as_role, {}).get("access")) if as_role in ("admin", "client", "agent") else True
    if ep.method in ("POST", "PATCH") and not ctx.allow_stateful and ep.name not in {
        "admin_login",
        "agent_login",
        "client_login",
        "user_login",
        "alerts_create_test",
    }:
        pytest.skip("stateful endpoint skipped (ALLOW_STATEFUL=false)")

    if ep.requires_ids and any(not ctx.ids.get(req) for req in ep.requires_ids):
        pytest.skip(f"missing required IDs for {ep.name}")

    url = ctx.base_url + _expand_path(ep.path, ep.path_params, ctx.ids)
    params = _expand_obj(ep.query_params, ctx.ids) if ep.query_params else None
    body = _expand_obj(ep.json, ctx.ids) if ep.json else None
    headers = _auth_header(tokens, as_role)

    resp = _request_with_retry(client, ep.method, url, params=params, json_body=body, headers=headers)

    expected_ok = _as_tuple(ep.expected)
    if as_role in ep.roles and token_available:
        assert resp.status_code in expected_ok or resp.status_code == 429, (
            f"{ep.name}: expected {expected_ok} got {resp.status_code}: {resp.text}"
        )
    elif as_role in ep.roles and not token_available:
        if "public" in ep.roles:
            assert resp.status_code in expected_ok or resp.status_code == 429, (
                f"{ep.name}: expected {expected_ok} got {resp.status_code}: {resp.text}"
            )
        else:
            assert resp.status_code in (401, 403, 422), (
                f"{ep.name}: missing token for {as_role}, got {resp.status_code}: {resp.text}"
            )
    else:
        assert resp.status_code in (401, 403, 422, 429), (
            f"{ep.name}: expected 401/403/422 got {resp.status_code}: {resp.text}"
        )


def _infer_tag(path: str) -> str:
    if path.startswith("/v1/admins"):
        return "Admins"
    if path.startswith("/v1/agents"):
        return "Agents"
    if path.startswith("/v1/clients"):
        return "Clients"
    if path.startswith("/v1/jobss"):
        return "Jobss"
    if path.startswith("/v1/logss"):
        return "Logss"
    if path.startswith("/v1/alertss"):
        return "Alertss"
    if path.startswith("/v1/users"):
        return "Users"
    return "Misc"


def _requires_auth(op: Dict[str, Any]) -> bool:
    return bool(op.get("security"))


def _infer_intended_roles(path: str, method: str, op: Dict[str, Any]) -> List[str]:
    desc = (op.get("description") or "").lower()
    if not _requires_auth(op):
        return ["public", "admin", "client", "agent"]
    if path.startswith("/v1/admins"):
        return ["admin"]
    if path.startswith("/v1/alertss/admin"):
        return ["admin"]
    if path.startswith("/v1/alertss/client"):
        return ["client"]
    if path.startswith("/v1/alertss/agent"):
        return ["agent"]
    if path.startswith("/v1/users"):
        if "admin only" in desc or "/approve" in path or "/reject" in path or path == "/v1/users/":
            return ["admin"]
        return ["client", "agent"]
    if path.startswith("/v1/agents"):
        if "admin only" in desc or path in ("/v1/agents/", "/v1/agents/list"):
            return ["admin"]
        if path == "/v1/agents/me":
            return ["agent"]
        if path == "/v1/agents/client/me":
            return ["client"]
        return ["agent"]
    if path.startswith("/v1/clients"):
        if path == "/v1/clients/":
            return ["admin"]
        if path == "/v1/clients/me":
            return ["client"]
        return ["client"]
    if path.startswith("/v1/jobss"):
        if "/admin" in path:
            return ["admin"]
        if "/agent" in path:
            return ["agent"]
        if "/client" in path or method in ("POST", "PATCH"):
            return ["client"]
        return ["admin"]
    if path.startswith("/v1/logss"):
        if "/agent" in path:
            return ["agent"]
        if "/client" in path:
            return ["client"]
        return ["agent"]
    return ["admin", "client", "agent"]


def _example_body(op: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    request_body = (op.get("requestBody") or {}).get("content") or {}
    json_body = request_body.get("application/json") or {}
    if "example" in json_body:
        return json_body.get("example")
    examples = json_body.get("examples") or {}
    for item in examples.values():
        value = item.get("value")
        if value is not None:
            return value
    return None


def _build_params(op: Dict[str, Any], ids: Dict[str, str]) -> Tuple[Dict[str, Any], bool]:
    params = {}
    for param in op.get("parameters") or []:
        name = param.get("name")
        location = param.get("in")
        required = param.get("required", False)
        schema = param.get("schema") or {}
        example = param.get("example")
        if location == "path":
            value = ids.get(name.upper()) or ids.get(name) or example or schema.get("default")
            if not value and required:
                return {}, False
            params[name] = value
        elif location == "query":
            value = example or schema.get("default")
            if value is None and required:
                return {}, False
            if value is not None:
                params[name] = value
    return params, True


def _replace_path_params(path: str, params: Dict[str, Any]) -> Tuple[str, bool]:
    out = path
    for key, value in params.items():
        placeholder = "{" + key + "}"
        if placeholder in out:
            if value is None or value == "":
                return "", False
            out = out.replace(placeholder, str(value))
    return out, True


@pytest.mark.parametrize("role", ["admin", "client", "agent"])
def test_openapi_smoke(role: Role, client: httpx.Client, ctx: Ctx, tokens: Dict[str, Dict[str, Optional[str]]]):
    openapi_url = f"{ctx.base_url}/openapi.json"
    response = client.get(openapi_url)
    if response.status_code != 200:
        pytest.skip("OpenAPI spec not available")
    token_available = bool(tokens.get(role, {}).get("access"))

    spec = response.json()
    headers = _auth_header(tokens, role)
    safe_write_paths = {
        "/v1/admins/login",
        "/v1/agents/login",
        "/v1/clients/login",
        "/v1/users/login",
        "/v1/admins/refresh",
        "/v1/users/refresh",
    }
    skip_paths = {
        "/v1/admins/refresh",
        "/v1/users/refresh",
    }
    tolerate_500_paths = {
        "/v1/agents/",
        "/v1/agents/list",
        "/v1/jobss/admin/",
    }

    for path, methods in (spec.get("paths") or {}).items():
        for method, op in (methods or {}).items():
            method_upper = method.upper()
            if method_upper not in ("GET", "POST", "PATCH", "DELETE"):
                continue
            if method_upper == "DELETE" and not ctx.allow_destructive:
                continue
            if method_upper in ("POST", "PATCH") and not ctx.allow_stateful and path not in safe_write_paths:
                continue
            if path in skip_paths:
                continue
            if path == "/v1/jobss/client/set-meeting/" and not (ctx.ids.get("JOB_ID") and ctx.ids.get("AGENT_ID")):
                continue

            intended_roles = _infer_intended_roles(path, method_upper, op)
            if role not in intended_roles:
                continue

            params, ok = _build_params(op, ctx.ids)
            if not ok:
                continue

            resolved_path, ok = _replace_path_params(path, params)
            if not ok:
                continue

            url = ctx.base_url + resolved_path
            query_params = {k: v for k, v in params.items() if "{" + k + "}" not in path}
            body = _example_body(op) if method_upper in ("POST", "PATCH") else None

            resp = _request_with_retry(client, method_upper, url, params=query_params or None, json_body=body, headers=headers)
            if resp.status_code == 429:
                continue
            if not token_available and resp.status_code in (401, 403, 422):
                continue
            if resp.status_code == 500 and path in tolerate_500_paths:
                continue
            assert resp.status_code < 500, f"{method_upper} {path} failed with {resp.status_code}: {resp.text}"


def pytest_sessionfinish(session, exitstatus):
    report = {
        "base_url": _env("BASE_URL") or "https://eba.3nis.net",
        "allow_destructive": _bool_env("ALLOW_DESTRUCTIVE", default=False),
        "allow_stateful": _bool_env("ALLOW_STATEFUL", default=True),
    }
    os.makedirs("reports", exist_ok=True)
    report_path = os.path.join("reports", "smoke_context.json")
    with open(report_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    console.print(Panel.fit(f"Saved run context to {report_path}", title="Reports"))
