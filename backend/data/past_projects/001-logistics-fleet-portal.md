---
id: 001-logistics-fleet-portal
title: Fleet Tracking Portal for a Logistics Operator
industry: logistics
stack: Angular, NestJS, PostgreSQL, Redis, AWS ECS
team_size: 5
duration_weeks: 20
total_hours: 3400
---

## Overview
Web portal for a regional logistics operator to track 600+ trucks in real time, manage drivers and review delivery KPIs. Dispatchers needed live map updates and alerts for route deviations.

## Scope and Estimates
- Auth, roles and multi-tenant organisation model: 160 h
- Live map with WebSocket vehicle positions (clustering, replay): 420 h
- Route deviation and idle alerts engine: 380 h
- Driver and vehicle management CRUD: 240 h
- KPI dashboards and CSV/PDF reports: 360 h
- Telematics provider integration (3 vendors, normalised events): 520 h
- DevOps, CI/CD, monitoring: 220 h
- QA, UAT and stabilisation: 700 h

## Tech Decisions
Angular with signals and a map library for the dispatcher UI. NestJS for the API, PostgreSQL with PostGIS for geo queries, Redis pub/sub for fanning out position updates to WebSocket clients. Telematics events were queued before processing to survive vendor bursts.

## Risks and Lessons
Vendor APIs differed in rate limits and payload formats, integration took 40% over the first estimate. Map clustering performance degraded above 2,000 markers until we moved clustering server side. Lesson: budget integrations separately and add a spike for every external vendor.
