from functools import lru_cache

from app.services.knowledge_service import KnowledgeService
from app.services.proposal_service import ProposalService


@lru_cache()
def get_knowledge_service() -> KnowledgeService:
    """Singleton: embedded Qdrant (local mode) must be opened by a single client."""
    return KnowledgeService()


@lru_cache()
def get_proposal_service() -> ProposalService:
    return ProposalService(knowledge=get_knowledge_service())
