import asyncio
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.deps import GenerationSlot, acquire_generation_slot, get_proposal_service
from app.schemas.proposal import ProposalRequest, ProposalResponse
from app.services.proposal_service import ProposalService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/proposals", tags=["Proposals"])


def _sse(event: str, data: object) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post(
    "/stream",
    summary="Generate Technical Proposal as a Server-Sent Events stream",
    description="Events: `references` (retrieved past projects), `section` ({key, value}, may be partial), "
                "`notice` ({fallback_model}, primary model failed), `complete` (final response) and `error`.",
    response_class=StreamingResponse,
)
async def stream_proposal(
    request: ProposalRequest,
    service: ProposalService = Depends(get_proposal_service),
    slot: GenerationSlot = Depends(acquire_generation_slot),
) -> StreamingResponse:
    slot.hand_over_to_stream()

    async def events():
        try:
            async for item in service.stream_proposal(request):
                yield _sse(item["event"], item["data"])
        except asyncio.CancelledError:
            raise  # client disconnected, let the upstream Gemini stream be closed
        except Exception:
            logger.exception("Proposal streaming failed")
            yield _sse("error", {"detail": "Failed to generate proposal. Please try again."})
        finally:
            slot.release()

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post(
    "/generate",
    response_model=ProposalResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Technical Proposal",
    description="Analyzes RFP client requirements, grounds estimates in similar past projects "
                "and returns a structured technical proposal.",
)
async def generate_proposal(
    request: ProposalRequest,
    service: ProposalService = Depends(get_proposal_service),
    _slot: GenerationSlot = Depends(acquire_generation_slot),
) -> ProposalResponse:
    try:
        return await service.generate_proposal(request)
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception:
        logger.exception("Proposal generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate proposal. Please try again.",
        )
