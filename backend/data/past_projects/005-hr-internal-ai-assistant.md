---
id: 005-hr-internal-ai-assistant
title: Internal HR Knowledge Assistant (RAG)
industry: hr
stack: Angular, FastAPI, Qdrant, OpenAI, Docker, Azure
team_size: 3
duration_weeks: 10
total_hours: 1500
---

## Overview
Chat assistant answering employee questions about policies, benefits and onboarding, grounded in 400 internal documents with source citations.

## Scope and Estimates
- Document ingestion (PDF, DOCX, Confluence), chunking, embeddings: 240 h
- Retrieval with metadata filters and reranking: 200 h
- Chat UI with streaming and citations (Angular): 260 h
- Access control: answers limited to documents the user may see: 180 h
- Evaluation set (60 questions) and quality dashboard: 160 h
- Usage, cost and latency monitoring: 80 h
- Deployment, SSO integration: 140 h
- QA and UAT: 240 h

## Tech Decisions
Qdrant with payload filters for permission-aware retrieval. Hybrid search (dense plus keyword) improved recall on policy names. Responses streamed over SSE.

## Risks and Lessons
Outdated policies produced confidently wrong answers, we added document versioning and freshness metadata. The evaluation set caught two regressions before release. Lesson: plan content ownership and evals before the first demo.
