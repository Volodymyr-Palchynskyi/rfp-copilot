---
id: 003-ecommerce-b2b-marketplace
title: B2B Marketplace for Industrial Parts
industry: ecommerce
stack: Angular, Node.js, Elasticsearch, PostgreSQL, Stripe, Azure
team_size: 7
duration_weeks: 30
total_hours: 6100
---

## Overview
Marketplace connecting industrial suppliers with buyers. 200k SKUs, per-customer price lists, quote requests and punch-out integration with buyer procurement systems.

## Scope and Estimates
- Catalogue import pipeline (CSV, XML, API feeds): 620 h
- Search and faceted filtering on Elasticsearch: 540 h
- Customer-specific pricing and quote workflow: 780 h
- Cart, checkout, Stripe Connect split payments: 700 h
- Supplier portal (inventory, orders, payouts): 820 h
- Buyer punch-out (cXML/OCI) integration: 480 h
- Admin back-office and moderation: 520 h
- Angular SSR for SEO, performance tuning: 340 h
- DevOps, load testing: 380 h
- QA and UAT: 920 h

## Tech Decisions
Angular SSR for product pages to keep organic traffic. Elasticsearch fed from PostgreSQL through an outbox pattern. Stripe Connect handled marketplace payouts and removed most of our compliance burden.

## Risks and Lessons
Supplier data quality was the largest hidden cost, feeds were inconsistent and needed manual mapping tools. Lesson: invest in an import validation UI from the start and treat data onboarding as a first-class workstream.
