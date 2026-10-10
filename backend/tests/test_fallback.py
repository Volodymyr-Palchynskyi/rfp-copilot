import json
from types import SimpleNamespace

import httpx
import pytest
from google.genai import errors

from app.core.config import settings
from app.schemas.proposal import ProposalRequest
from app.services.proposal_service import ProposalService, is_retryable

DRAFT = {
    "project_title": "T",
    "executive_summary": "S",
    "architecture_overview": "A",
    "tech_stack": [],
    "features": [{"module": "m", "title": "t", "description": "d", "complexity": "low", "hours_min": 10, "hours_max": 20}],
    "risks": [],
    "estimated_duration_weeks": 4,
    "estimation_basis": "none",
}
USAGE = SimpleNamespace(prompt_token_count=1, candidates_token_count=2, thoughts_token_count=3, total_token_count=6)
REQUEST = ProposalRequest(client_name="Acme", project_description="A project description long enough.")


def api_error(code: int) -> errors.APIError:
    return errors.APIError(code, {"error": {"message": "boom"}})


class FakeModels:
    """Behaviour per model name: an exception to raise, or JSON text to return."""

    def __init__(self, behaviour: dict[str, Exception | str]) -> None:
        self.behaviour = behaviour
        self.calls: list[str] = []

    async def generate_content(self, model, contents, config):
        self.calls.append(model)
        outcome = self.behaviour[model]
        if isinstance(outcome, Exception):
            raise outcome
        return SimpleNamespace(text=outcome, usage_metadata=USAGE)

    async def generate_content_stream(self, model, contents, config):
        self.calls.append(model)
        outcome = self.behaviour[model]
        if isinstance(outcome, Exception):
            raise outcome

        async def chunks():
            yield SimpleNamespace(text=outcome[:20], usage_metadata=None)
            yield SimpleNamespace(text=outcome[20:], usage_metadata=USAGE)

        return chunks()


def make_service(monkeypatch, behaviour, fallback="backup-model") -> tuple[ProposalService, FakeModels]:
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(settings, "GEMINI_MODEL", "primary-model")
    monkeypatch.setattr(settings, "GEMINI_FALLBACK_MODEL", fallback)
    service = ProposalService(knowledge=None)
    fake = FakeModels(behaviour)
    service.client = SimpleNamespace(aio=SimpleNamespace(models=fake))
    return service, fake


@pytest.mark.parametrize(
    "exc, expected",
    [
        (api_error(429), True),
        (api_error(503), True),
        (api_error(400), False),
        (api_error(403), False),
        (httpx.ReadTimeout("slow"), True),
        (ValueError("bug"), False),
    ],
)
def test_is_retryable(exc, expected):
    assert is_retryable(exc) is expected


async def test_generate_falls_back_on_rate_limit(monkeypatch):
    service, fake = make_service(monkeypatch, {"primary-model": api_error(429), "backup-model": json.dumps(DRAFT)})

    response = await service.generate_proposal(REQUEST)

    assert fake.calls == ["primary-model", "backup-model"]
    assert response.usage.model == "backup-model"
    assert response.total_hours_min == 10


async def test_generate_does_not_fall_back_on_client_error(monkeypatch):
    service, fake = make_service(monkeypatch, {"primary-model": api_error(400), "backup-model": json.dumps(DRAFT)})

    with pytest.raises(errors.APIError):
        await service.generate_proposal(REQUEST)
    assert fake.calls == ["primary-model"]


async def test_no_fallback_configured_raises(monkeypatch):
    service, fake = make_service(monkeypatch, {"primary-model": api_error(503)}, fallback="")

    with pytest.raises(errors.APIError):
        await service.generate_proposal(REQUEST)
    assert fake.calls == ["primary-model"]


async def test_stream_falls_back_before_first_token_and_emits_notice(monkeypatch):
    service, fake = make_service(monkeypatch, {"primary-model": api_error(503), "backup-model": json.dumps(DRAFT)})

    events = [e async for e in service.stream_proposal(REQUEST)]

    kinds = [e["event"] for e in events]
    assert kinds[0] == "references" and "notice" in kinds and kinds[-1] == "complete"
    assert next(e for e in events if e["event"] == "notice")["data"] == {"fallback_model": "backup-model"}
    assert events[-1]["data"]["usage"]["model"] == "backup-model"
    assert fake.calls == ["primary-model", "backup-model"]


async def test_stream_fails_when_all_models_fail(monkeypatch):
    service, _ = make_service(monkeypatch, {"primary-model": api_error(503), "backup-model": api_error(500)})

    with pytest.raises(errors.APIError):
        _ = [e async for e in service.stream_proposal(REQUEST)]
