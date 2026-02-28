# DAIL Backend — Implementation Plan

## Overview

This document details the phased implementation plan for modernizing the **Database of AI Litigation (DAIL)** from its current Caspio/WordPress architecture to a production-grade **FastAPI + PostgreSQL** backend.

---

## Phase 1: Foundation (Weeks 1–2)

### 1.1 Infrastructure Setup
- [x] PostgreSQL 16 database with JSONB & tsvector support
- [x] Redis for caching and rate limiting
- [x] Docker Compose for local development
- [x] Alembic migration framework

### 1.2 Core Data Model
- [x] All 13 database models (Court, Case, Docket, Opinion, Citation, Party, Judge, Document, SecondarySource, AIClassification, AuditLog, Provenance)
- [x] Full-text search via GIN-indexed tsvector columns
- [x] JSONB arrays for flexible classification storage
- [x] Soft deletes and version chains for legal audit compliance
- [x] Automatic search vector triggers

### 1.3 API Layer
- [x] FastAPI with versioned routes (`/api/v1/`)
- [x] Full CRUD for all entities
- [x] Pydantic validation schemas with computed fields
- [x] Pagination, filtering, and sorting on all list endpoints
- [x] OpenAPI documentation auto-generated

---

## Phase 2: Data Migration (Weeks 3–4)

### 2.1 Caspio XLSX Import
- [x] `scripts/migrate_caspio.py` — reads the 4 existing Excel exports
- [x] Field-by-field mapping from Caspio column names → new schema
- [x] Provenance tracking for every migrated record
- [x] Duplicate detection by `record_number`

### 2.2 Data Integrity Validation
- [ ] Post-migration audit: row counts, field completeness
- [ ] Cross-reference validation across Cases ↔ Dockets ↔ Documents
- [ ] Generate migration report with discrepancy log

### 2.3 Court Seeding
- [x] `scripts/seed_courts.py` — 23 federal courts pre-loaded
- [ ] Extend with state courts as needed

---

## Phase 3: CourtListener Integration (Weeks 5–6)

### 3.1 API Client
- [x] Async HTTP client with token authentication
- [x] Rate limit handling (5,000 queries/hour, Retry-After support)
- [x] Exponential backoff retries (3 attempts max)
- [x] Endpoints: dockets, opinions, RECAP, citations, people, courts

### 3.2 Enrichment Pipeline
- [x] `ingestion_service.enrich_case_from_courtlistener()` — links CL docket data
- [x] Provenance records for all CourtListener-sourced data
- [x] Citation verification via CL lookup endpoint

### 3.3 Automated Monitoring
- [x] Celery Beat hourly polling for new AI-related filings
- [x] Keyword-based search across 10 AI litigation terms
- [ ] Alert system for new high-relevance matches

---

## Phase 4: NLP & Classification (Weeks 7–8)

### 4.1 Rule-Based Classification
- [x] 15 AI technology type patterns (facial recognition, generative AI, etc.)
- [x] 11 legal theory patterns (due process, discrimination, copyright, etc.)
- [x] 8 industry sector patterns
- [x] Confidence scoring per classification

### 4.2 Citation Extraction
- [x] eyecite integration for gold-standard extraction
- [x] Regex fallback for basic citations
- [x] CourtListener verification of extracted citations
- [ ] Citation graph construction

### 4.3 Entity Resolution
- [x] Jaro-Winkler name similarity matching
- [x] Entity suffix normalization (Corp, Inc, LLC, etc.)
- [x] Canonical ID chains for deduplication
- [ ] Batch resolution pipeline for full database

---

## Phase 5: Search & Analytics (Weeks 9–10)

### 5.1 Full-Text Search
- [x] PostgreSQL tsvector with weighted A/B/C/D fields
- [x] GIN indexes for fast lookups
- [x] ILIKE fallback when tsvector unavailable
- [ ] Elasticsearch integration for advanced search (future)

### 5.2 Analytics Dashboard API
- [x] Aggregate statistics endpoint (`/api/v1/analytics/summary`)
- [x] Breakdowns: status, jurisdiction, area, AI tech, legal theory, year
- [x] Most active jurisdictions ranking
- [x] Recent cases timeline

---

## Phase 6: Production Hardening (Weeks 11–12)

### 6.1 Security
- [x] API key authentication middleware
- [x] Redis-based rate limiting (per-minute and per-hour)
- [x] CORS configuration
- [x] Request ID correlation for audit trails

### 6.2 Observability
- [x] structlog structured logging
- [x] Sentry error tracking integration
- [x] Audit log for all data modifications
- [x] Request timing in middleware

### 6.3 Deployment
- [x] Multi-stage Dockerfile (builder + production)
- [x] Docker Compose with all services
- [x] Health check endpoint
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Staging environment setup

---

## Data Flow Architecture

```
Caspio XLSX ──→ migrate_caspio.py ──→ PostgreSQL ←──→ FastAPI API
                                          ↑
CourtListener API ──→ courtlistener.py ───┘
                                          ↓
                                    Celery Worker
                                    ├── Classification
                                    ├── Citation extraction
                                    └── Search vector updates
```

---

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | FastAPI | Async, type-safe, auto-docs |
| Database | PostgreSQL 16 | JSONB, tsvector, GIN indexes |
| ORM | SQLAlchemy 2.0 async | Industry standard, Alembic integration |
| Task queue | Celery + Redis | Proven, scalable |
| Citation parsing | eyecite | Gold standard, developed by Free Law Project |
| Rate limiting | Redis sliding window | Efficient, distributed-ready |
| Deployment | Docker Compose | Reproducible, multi-service |
