import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import get_knowledge_service
from app.api.v1.router import api_router
from app.core.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Index the knowledge base on first start. Best effort: the API still boots without it."""
    try:
        await get_knowledge_service().ensure_indexed()
    except Exception:
        logger.exception("Knowledge base indexing failed, proposals will be generated without RAG context")
    yield


# ==============================================================================
# APPLICATION BOOTSTRAP
# ==============================================================================
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-driven Technical Proposal and Scope of Work Generator",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ==============================================================================
# CORS MIDDLEWARE
# ==============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# ROUTER REGISTRATION
# ==============================================================================
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["System"])
async def health_check():
    """Liveness probe for monitoring and container orchestration."""
    return {"status": "ok", "project": settings.PROJECT_NAME, "version": settings.VERSION}


# ==============================================================================
# LOCAL RUNNER
# ==============================================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)