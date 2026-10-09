---
id: 006-saas-analytics-dashboard
title: Embedded Analytics Dashboard for a SaaS Product
industry: saas
stack: Angular, Python, ClickHouse, Kafka, Terraform, AWS
team_size: 6
duration_weeks: 24
total_hours: 4600
---

## Overview
Customer-facing analytics module embedded in an existing SaaS product: configurable dashboards, scheduled reports and near real-time metrics over billions of events.

## Scope and Estimates
- Event ingestion via Kafka, schema registry: 520 h
- ClickHouse modelling, aggregation jobs: 640 h
- Query API with tenant isolation and caching: 560 h
- Dashboard builder (drag and drop widgets, Angular): 1,000 h
- Scheduled reports, email and PDF export: 380 h
- Infrastructure as code, observability: 440 h
- Performance and load testing: 300 h
- QA and rollout: 760 h

## Tech Decisions
ClickHouse materialised views for common aggregates, Angular CDK for the drag and drop grid, per-tenant row policies for isolation.

## Risks and Lessons
Dashboard builder UX iterations consumed 30% more than planned. High-cardinality queries needed guardrails and timeouts. Lesson: prototype the builder with real users before committing to a fixed estimate.
