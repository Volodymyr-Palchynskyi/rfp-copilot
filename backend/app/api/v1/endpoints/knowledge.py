import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_knowledge_service, limit_searches, require_admin
from app.schemas.knowledge import ChunkHit, IngestResult
from app.services.knowledge_service import KnowledgeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge", tags=["Knowledge base"])


@router.post(
    "/ingest",
    response_model=IngestResult,
    summary="Rebuild the vector index from past project documents (requires X-Admin-Token)",
    dependencies=[Depends(require_admin)],
)
async def ingest(service: KnowledgeService = Depends(get_knowledge_service)) -> IngestResult:
    try:
        return await service.ingest()
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except Exception:
        logger.exception("Ingestion failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ingestion failed.")


@router.get(
    "/search",
    response_model=list[ChunkHit],
    summary="Semantic search over past projects (debugging and transparency)",
    dependencies=[Depends(limit_searches)],
)
async def search(
    q: str = Query(min_length=3, description="Natural language query"),
    limit: int = Query(default=5, ge=1, le=20),
    service: KnowledgeService = Depends(get_knowledge_service),
) -> list[ChunkHit]:
    try:
        return await service.search(q, limit)
    except Exception:
        logger.exception("Search failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Search failed.")
