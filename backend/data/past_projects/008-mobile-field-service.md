---
id: 008-mobile-field-service
title: Offline-First Field Service App for Technicians
industry: field-service
stack: Ionic Angular, NestJS, PostgreSQL, SQLite, Azure
team_size: 5
duration_weeks: 21
total_hours: 3600
---

## Overview
Mobile app for technicians to receive jobs, record work, capture photos and signatures in areas without connectivity, with back-office scheduling.

## Scope and Estimates
- Offline data layer with sync and conflict resolution: 760 h
- Job list, details, checklists, forms: 520 h
- Photo and signature capture, upload queue: 300 h
- Scheduling and dispatch web console: 640 h
- ERP integration (jobs, parts, invoices): 520 h
- Push notifications and background sync: 200 h
- DevOps, device testing, store release: 260 h
- QA and field pilot: 400 h

## Tech Decisions
Ionic with Angular to reuse web skills, SQLite local store, server-wins with field-level merge for conflicts, resumable uploads.

## Risks and Lessons
Conflict resolution and sync edge cases were the biggest source of defects. Device fragmentation added testing time. Lesson: treat offline sync as its own epic with a dedicated test matrix and add 25% buffer.
