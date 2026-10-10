import pytest
from fastapi.testclient import TestClient

from app.api import deps
from app.core.config import settings
from app.core.limits import ConcurrencyGate, SlidingWindowLimiter
from app.main import app
from app.schemas.proposal import ProposalDraft

BRIEF = "A web portal for tracking service vans with live map and alerts."
PAYLOAD = {"client_name": "Acme", "project_description": BRIEF}


class FakeProposalService:
    """Stands in for Gemini: one event, then done."""

    async def stream_proposal(self, request):
        yield {"event": "references", "data": []}

    async def generate_proposal(self, request):
        raise AssertionError("not used in these tests")


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(deps, "_generation_limiter", SlidingWindowLimiter(2, 600))
    monkeypatch.setattr(deps, "_search_limiter", SlidingWindowLimiter(2, 600))
    monkeypatch.setattr(deps, "_generation_gate", ConcurrencyGate(1))
    app.dependency_overrides[deps.get_proposal_service] = FakeProposalService
    # No `with`: skips the lifespan, which would try to index the knowledge base.
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_stream_returns_events(client):
    response = client.post("/api/v1/proposals/stream", json=PAYLOAD)
    assert response.status_code == 200
    assert "event: references" in response.text


def test_rate_limit_returns_429_with_retry_after(client):
    for _ in range(2):
        assert client.post("/api/v1/proposals/stream", json=PAYLOAD).status_code == 200

    blocked = client.post("/api/v1/proposals/stream", json=PAYLOAD)
    assert blocked.status_code == 429
    assert int(blocked.headers["retry-after"]) >= 1
    assert "Rate limit" in blocked.json()["detail"]


def test_slot_is_released_after_stream_ends(client):
    # Gate allows 1 concurrent generation, so sequential requests only pass if slots are freed.
    for _ in range(2):
        assert client.post("/api/v1/proposals/stream", json=PAYLOAD).status_code == 200
    assert deps._generation_gate.active == 0


def test_busy_service_returns_503(client):
    assert deps._generation_gate.try_acquire() is not None  # someone else is generating
    response = client.post("/api/v1/proposals/stream", json=PAYLOAD)
    assert response.status_code == 503


def test_brief_too_long_is_rejected(client):
    long_brief = {**PAYLOAD, "project_description": "x" * (settings.MAX_BRIEF_CHARS + 1)}
    assert client.post("/api/v1/proposals/stream", json=long_brief).status_code == 422


def test_ingest_disabled_without_admin_token(client, monkeypatch):
    monkeypatch.setattr(settings, "ADMIN_TOKEN", "")
    assert client.post("/api/v1/knowledge/ingest").status_code == 403


def test_ingest_rejects_wrong_token(client, monkeypatch):
    monkeypatch.setattr(settings, "ADMIN_TOKEN", "secret")
    assert client.post("/api/v1/knowledge/ingest").status_code == 401
    assert client.post("/api/v1/knowledge/ingest", headers={"X-Admin-Token": "nope"}).status_code == 401
