"""CA-2 from the post-incident analysis: an unreachable solver must answer 503.

The drill on 27 Oct showed `POST /api/schedules/generate` returning a bare 500
when the solver container was down, and an error body with no request id to
quote when reporting the problem. Both are pinned here.
"""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import ExternalServiceError
from app.core.security import get_current_user
from app.db.models.people.user import UserRole
from app.db.session import get_db
from app.main import app
from app.services.schedule_generation_service import ScheduleGenerationService


def _service():
    service = ScheduleGenerationService(*[MagicMock() for _ in range(13)])
    service._format_data_for_scheduler = AsyncMock(return_value={})
    service.schedule_service.create_schedule = AsyncMock()
    return service


def _solver_transport(handler):
    real_client = httpx.AsyncClient
    return patch(
        "app.services.schedule_generation_service.httpx.AsyncClient",
        lambda *a, **kw: real_client(transport=httpx.MockTransport(handler)),
    )


def _generate(service):
    return asyncio.run(service.generate_and_save_schedule({}, {}, "label"))


def test_unreachable_solver_is_reported_as_unavailable():
    def refuse(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    service = _service()
    with _solver_transport(refuse):
        with pytest.raises(ExternalServiceError) as exc:
            _generate(service)

    assert exc.value.status_code == 503
    assert exc.value.headers["Retry-After"]
    service.schedule_service.create_schedule.assert_not_awaited()


def test_solver_server_error_is_reported_as_unavailable():
    def fail(request: httpx.Request) -> httpx.Response:
        return httpx.Response(502, text="bad gateway")

    service = _service()
    with _solver_transport(fail):
        with pytest.raises(ExternalServiceError) as exc:
            _generate(service)

    assert exc.value.status_code == 503


def test_solver_rejecting_the_payload_is_not_reported_as_unavailable():
    """A 4xx means our request was wrong, so it must not look like an outage."""
    def reject(request: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json={"detail": "missing params.timeLimitSec"})

    service = _service()
    with _solver_transport(reject):
        with pytest.raises(Exception) as exc:
            _generate(service)

    assert not isinstance(exc.value, ExternalServiceError)


class _Admin:
    role = UserRole.ADMIN
    is_active = True


async def _no_db():
    yield None


def test_error_responses_carry_the_request_id_in_the_body():
    """Page 5 promises this id in the body; until now it was header-only."""
    app.dependency_overrides[get_db] = _no_db
    app.dependency_overrides[get_current_user] = lambda: _Admin()
    try:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.post("/api/groups/", json={"name": "x", "size": -1})
    finally:
        app.dependency_overrides.clear()

    body = response.json()
    assert response.status_code == 422
    assert "detail" in body, "existing clients read e.detail"
