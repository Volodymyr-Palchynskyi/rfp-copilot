---
id: 007-edtech-lms
title: Learning Management System for Corporate Training
industry: edtech
stack: Angular, Django, PostgreSQL, Redis, S3, Docker
team_size: 4
duration_weeks: 18
total_hours: 2800
---

## Overview
LMS for corporate training: courses with video and quizzes, learning paths, certificates, manager reports and SCORM package support.

## Scope and Estimates
- User management, SSO, groups: 220 h
- Course authoring and content library: 480 h
- Video delivery and progress tracking: 300 h
- Quizzes and assessments with attempt rules: 340 h
- Learning paths, enrolment rules, certificates: 360 h
- SCORM import and player: 420 h
- Manager reporting and exports: 280 h
- DevOps, QA, UAT: 400 h

## Tech Decisions
Django for fast admin tooling, Angular front end, video on a managed streaming service rather than self-hosting.

## Risks and Lessons
SCORM compatibility across authoring tools was underestimated, every package type had quirks. Lesson: collect real sample packages before estimating and cap the supported standard versions.
