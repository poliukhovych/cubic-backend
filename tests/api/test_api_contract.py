"""Characterization and regression tests for the HTTP contract.

CS-61 pins the v1.0 behaviour that must not change silently; CS-71 checks that
the v1.0 scenarios still resolve after the v2.0 account-approval work. Both read
the generated OpenAPI document, so a removed or renamed route fails the build
instead of surfacing as a 404 in the browser.
"""
import pytest
from fastapi.testclient import TestClient

from app.core.security import get_current_user
from app.db.models.people.user import UserRole
from app.db.session import get_db
from app.main import app

# Routes the v1.0 scenarios depend on: admin login, catalog CRUD,
# schedule generation and schedule viewing.
V1_CONTRACT = {
    ("POST", "/api/auth/admin/login"),
    ("POST", "/api/auth/login"),
    ("GET", "/api/auth/me"),
    ("POST", "/api/schedules/generate"),
    ("GET", "/api/schedules/latest"),
    ("GET", "/api/schedules/{schedule_id}"),
    ("GET", "/api/students/{student_id}/schedule"),
    ("GET", "/api/teachers/{teacher_id}/schedule"),
    ("GET", "/api/groups/"),
    ("POST", "/api/groups/"),
    ("PUT", "/api/groups/{group_id}"),
    ("DELETE", "/api/groups/{group_id}"),
    ("GET", "/api/courses/"),
    ("POST", "/api/courses/"),
    ("PUT", "/api/courses/{course_id}"),
    ("DELETE", "/api/courses/{course_id}"),
    ("GET", "/api/teachers/"),
    ("POST", "/api/teachers/"),
    ("PUT", "/api/teachers/{teacher_id}"),
    ("DELETE", "/api/teachers/{teacher_id}"),
    ("GET", "/api/rooms/"),
    ("GET", "/api/timeslots/"),
    ("GET", "/api/users/"),
    ("GET", "/health/"),
}

# Added by v2.0: registration lifecycle and account activation.
V2_CONTRACT = {
    ("POST", "/api/auth/register/{role}"),
    ("GET", "/api/admin/registrations/"),
    ("PUT", "/api/admin/registrations/{request_id}"),
    ("PATCH", "/api/admin/registrations/{request_id}/approve"),
    ("PATCH", "/api/admin/registrations/{request_id}/reject"),
    ("PATCH", "/api/admin/students/{student_id}/activate"),
    ("PATCH", "/api/admin/students/{student_id}/deactivate"),
    ("PATCH", "/api/admin/teachers/{teacher_id}/activate"),
    ("PATCH", "/api/admin/teachers/{teacher_id}/deactivate"),
}


def _published_operations():
    spec = app.openapi()
    return {
        (method.upper(), path)
        for path, operations in spec["paths"].items()
        for method in operations
        if method in ("get", "post", "put", "patch", "delete")
    }


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = _no_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_current_user, None)


async def _no_db():
    yield None


def test_v1_contract_survives_on_the_current_code():
    missing = sorted(V1_CONTRACT - _published_operations())

    assert missing == [], f"v1.0 routes disappeared: {missing}"


def test_v2_account_approval_contract_is_published():
    missing = sorted(V2_CONTRACT - _published_operations())

    assert missing == [], f"v2.0 routes missing: {missing}"


def test_validation_errors_never_echo_the_submitted_payload(client):
    """A 422 must not mirror the request body back: it may carry a password."""
    secret = "sup3r-secret-value"

    response = client.post("/api/auth/login", json={"password": secret})

    assert response.status_code == 422
    body = response.text
    assert secret not in body
    for error in response.json()["detail"]:
        assert set(error) <= {"type", "loc", "msg"}


def test_every_api_response_is_traceable_by_request_id(client):
    """CS-45: the request id returned here is what the log search is keyed on."""
    app.dependency_overrides[get_current_user] = lambda: _FakeAdmin()

    response = client.post("/api/groups/", json={"name": ""})

    assert response.status_code == 422
    assert response.headers.get("X-Request-ID")
    assert response.headers.get("X-Process-Time")


class _FakeAdmin:
    role = UserRole.ADMIN
    is_active = True
