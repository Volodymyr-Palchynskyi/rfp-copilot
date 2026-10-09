---
id: 004-healthcare-patient-app
title: Patient Appointment and Telehealth App
industry: healthcare
stack: Flutter, FastAPI, PostgreSQL, Twilio Video, GCP
team_size: 5
duration_weeks: 22
total_hours: 3900
---

## Overview
Mobile and web app for a clinic network: appointment booking, video consultations, prescription reminders and secure messaging with doctors.

## Scope and Estimates
- Patient mobile app (Flutter, iOS and Android): 900 h
- Appointment scheduling with doctor calendars and conflicts: 520 h
- Video consultation with Twilio, fallback handling: 380 h
- Secure messaging and notifications (push, SMS, email): 420 h
- Doctor web dashboard: 560 h
- EHR system integration via HL7 FHIR: 480 h
- HIPAA-aligned security, audit logging: 300 h
- QA, store submission, UAT: 340 h

## Tech Decisions
Single FastAPI backend serving the app and dashboard. FHIR integration isolated behind an anti-corruption layer so the clinic EHR vendor could change. All access to patient data logged.

## Risks and Lessons
EHR vendor provided limited test data and slow support, integration slipped two weeks. App store review for health apps required extra documentation. Lesson: start vendor onboarding and store review preparation in the first month.
