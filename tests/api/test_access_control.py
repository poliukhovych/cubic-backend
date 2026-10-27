"""Access-control checks for QR-1.

QR-1: a non-admin JWT on /api/admin/* must get 403, a request with no token 401.

The database dependency is overridden with a stub, so these tests describe the
authorization layer only and need no PostgreSQL.
"""
import pytest
from fastapi.testclient import TestClient

from app.core.security import get_current_user
from app.db.models.people.user import UserRole
from app.db.session import get_db
from app.main import app

ADMIN_ENDPOINTS = [
    "/api/admin/stats",
    "/api/admin/students",
    "/api/admin/teachers",
    "/api/admin/registrations/",
]


class _User:
    """Minimal stand-in for the User model: require_role only reads .role."""

    def __init__(self, role: UserRole):
        self.role = role
        self.is_active = True


async def _no_db():
    yield None


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = _no_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.parametrize("endpoint", ADMIN_ENDPOINTS)
def test_admin_endpoints_reject_anonymous_callers(client, endpoint):
    assert client.get(endpoint).status_code == 401


@pytest.mark.parametrize("endpoint", ADMIN_ENDPOINTS)
@pytest.mark.parametrize("role", [UserRole.STUDENT, UserRole.TEACHER])
def test_admin_endpoints_reject_non_admin_roles(client, endpoint, role):
    app.dependency_overrides[get_current_user] = lambda: _User(role)

    assert client.get(endpoint).status_code == 403


def test_catalog_write_requires_authentication(client):
    payload = {"name": "Test group", "size": 30, "type": "bachelor", "course": 1}

    assert client.post("/api/groups/", json=payload).status_code == 401


@pytest.mark.parametrize(
    "payload, reason",
    [
        ({"name": "", "size": 30, "type": "bachelor", "course": 1}, "empty name"),
        ({"name": "G", "size": 0, "type": "bachelor", "course": 1}, "size must be > 0"),
        ({"name": "G", "size": 30, "type": "bachelor", "course": 9}, "course out of range"),
        ({"name": "G", "size": 30, "type": "doctoral", "course": 1}, "unknown type"),
    ],
)
def test_group_payload_is_validated_before_any_write(client, payload, reason):
    app.dependency_overrides[get_current_user] = lambda: _User(UserRole.ADMIN)

    assert client.post("/api/groups/", json=payload).status_code == 422, reason
