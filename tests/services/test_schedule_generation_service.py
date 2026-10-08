import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.core.exceptions import ValidationError
from app.services.schedule_generation_service import ScheduleGenerationService


def _service():
    service = ScheduleGenerationService(*[MagicMock() for _ in range(13)])
    service._format_data_for_scheduler = AsyncMock(return_value={})
    service.schedule_service.create_schedule = AsyncMock()
    return service


def _solver(result: dict):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/solve":
            return httpx.Response(200, json={"jobId": "job-1"})
        return httpx.Response(200, json=result)

    real_client = httpx.AsyncClient
    return patch(
        "app.services.schedule_generation_service.httpx.AsyncClient",
        lambda *a, **kw: real_client(transport=httpx.MockTransport(handler)),
    )


@pytest.mark.parametrize(
    "result",
    [
        {"status": "infeasible", "assignments": []},
        {"status": "solved", "assignments": []},
    ],
)
def test_failed_generation_does_not_create_schedule(result):
    service = _service()

    with _solver(result), patch(
        "app.services.schedule_generation_service.asyncio.sleep", AsyncMock()
    ):
        with pytest.raises(ValidationError) as exc:
            asyncio.run(service.generate_and_save_schedule({}, {}, "label"))

    assert exc.value.status_code == 422
    service.schedule_service.create_schedule.assert_not_awaited()
