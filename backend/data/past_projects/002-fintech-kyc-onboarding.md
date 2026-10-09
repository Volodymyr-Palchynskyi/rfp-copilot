---
id: 002-fintech-kyc-onboarding
title: KYC Onboarding Platform for a Digital Bank
industry: fintech
stack: React, FastAPI, PostgreSQL, Celery, S3, Kubernetes
team_size: 6
duration_weeks: 26
total_hours: 5200
---

## Overview
Customer onboarding flow for a challenger bank: document capture, identity verification, sanctions screening and a manual review queue for compliance officers.

## Scope and Estimates
- Customer-facing onboarding wizard with document capture: 480 h
- Integration with identity verification vendor (webhooks, retries): 460 h
- Sanctions and PEP screening integration: 340 h
- Compliance officer review console with audit trail: 720 h
- Rules engine for risk scoring: 560 h
- Encryption, PII handling, GDPR data retention: 420 h
- Admin and reporting: 380 h
- Infrastructure, security hardening, pen-test fixes: 640 h
- QA, regulatory sign-off support: 1,200 h

## Tech Decisions
FastAPI with async workers via Celery for vendor calls. Documents in S3 with per-object encryption keys. Every decision made by a human or the rules engine was written to an append-only audit table.

## Risks and Lessons
Regulatory requirements changed mid-project and added about 8 weeks. Vendor sandbox behaved differently from production. Lesson: reserve at least 15% contingency for compliance-driven scope and negotiate a production-like sandbox early.
