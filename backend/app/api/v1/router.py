from fastapi import APIRouter
from app.api.v1.endpoints import knowledge, proposals

api_router = APIRouter()

# Register feature routers under v1
api_router.include_router(proposals.router)
api_router.include_router(knowledge.router)
