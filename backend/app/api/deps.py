import hmac
from collections.abc import Iterator
from functools import lru_cache

from fastapi import Depends, Header, HTTPException, Request, status

from app.core.config import settings
from app.core.limits import ConcurrencyGate, SlidingWindowLimiter
from app.services.knowledge_service import KnowledgeService
from app.services.proposal_service import ProposalService


@lru_cache()
def get_knowledge_service() -> KnowledgeService:
    """Singleton: embedded Qdrant (local mode) must be opened by a single client."""
    return KnowledgeService()


@lru_cache()
def get_proposal_service() -> ProposalService:
    return ProposalService(knowledge=get_knowledge_service())


# ------------------------------------------------------------------ abuse protection
_generation_limiter = SlidingWindowLimiter(settings.RATE_LIMIT_GENERATIONS, settings.RATE_LIMIT_WINDOW_S)
_search_limiter = SlidingWindowLimiter(settings.RATE_LIMIT_SEARCHES, settings.RATE_LIMIT_WINDOW_S)
_generation_gate = ConcurrencyGate(settings.MAX_CONCURRENT_GENERATIONS)


def _client_key(request: Request) -> str:
    # Behind a reverse proxy run uvicorn with --proxy-headers so this is the real client IP.
    return request.client.host if request.client else "unknown"


def _enforce(limiter: SlidingWindowLimiter, request: Request) -> None:
    retry_after = limiter.check(_client_key(request))
    if retry_after is not None:
        seconds = max(1, int(retry_after) + 1)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit reached. Try again in {seconds} s.",
            headers={"Retry-After": str(seconds)},
        )


def limit_generations(request: Request) -> None:
    _enforce(_generation_limiter, request)


def limit_searches(request: Request) -> None:
    _enforce(_search_limiter, request)


class GenerationSlot:
    """
    One of the concurrent-generation slots. Plain endpoints just let the dependency release it.
    Streaming endpoints call `hand_over_to_stream()` and release it themselves when the stream ends,
    because the dependency cleanup may run before the response body has finished.
    """

    def __init__(self, slot_id: int) -> None:
        self._slot_id = slot_id
        self._released = False
        self.owned_by_stream = False

    def hand_over_to_stream(self) -> None:
        self.owned_by_stream = True

    def release(self) -> None:
        if not self._released:
            self._released = True
            _generation_gate.release(self._slot_id)


def acquire_generation_slot(_: None = Depends(limit_generations)) -> Iterator[GenerationSlot]:
    slot_id = _generation_gate.try_acquire()
    if slot_id is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The service is busy generating other proposals. Please retry in a moment.",
            headers={"Retry-After": "15"},
        )
    slot = GenerationSlot(slot_id)
    try:
        yield slot
    finally:
        if not slot.owned_by_stream:
            slot.release()


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    if not settings.ADMIN_TOKEN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Administrative endpoints are disabled.")
    if not x_admin_token or not hmac.compare_digest(x_admin_token, settings.ADMIN_TOKEN):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid admin token.")
