from pydantic import BaseModel, Field


class ChunkHit(BaseModel):
    score: float = Field(description="Cosine similarity between query and chunk")
    project_id: str
    title: str
    section: str
    text: str


class IngestResult(BaseModel):
    projects: int
    chunks: int
