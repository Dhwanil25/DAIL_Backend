# DAIL Backend — Architecture

## System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                       CLIENTS                             │
│  React Frontend │ Postman │ Research Scripts │ WordPress  │
└────────────────────────┬─────────────────────────────────┘
                         │ HTTPS
┌────────────────────────▼─────────────────────────────────┐
│                    FastAPI Application                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │Rate Limit│  │  Audit   │  │  CORS    │  │  GZip    │ │
│  │Middleware│  │Middleware │  │ Middleware│  │Middleware │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
│                                                           │
│  ┌─── API v1 ──────────────────────────────────────────┐ │
│  │ /cases  /courts  /dockets  /opinions  /citations    │ │
│  │ /parties  /judges  /documents  /secondary-sources   │ │
│  │ /search  /analytics  /health                        │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌─── Services Layer ──────────────────────────────────┐ │
│  │ CourtListenerClient  │ CitationService               │ │
│  │ SearchService        │ ClassificationService          │ │
│  │ EntityResolution     │ IngestionService               │ │
│  └─────────────────────────────────────────────────────┘ │
└──────┬───────────────────────┬───────────────────────────┘
       │                       │
       ▼                       ▼
┌──────────────┐       ┌──────────────┐
│ PostgreSQL 16│       │  Redis 7     │
│              │       │              │
│ 13 tables    │       │ Rate limits  │
│ GIN indexes  │       │ Cache        │
│ tsvector FTS │       │ Celery broker│
│ JSONB columns│       │              │
└──────────────┘       └──────┬───────┘
                              │
                       ┌──────▼───────┐
                       │Celery Worker │
                       │              │
                       │ Ingestion    │
                       │ Classification│
                       │ Sync tasks   │
                       └──────────────┘
```

## Database Schema (13 Tables)

### Core Entities
- **courts** — Federal and state court definitions, linked to CourtListener
- **cases** — Central entity preserving all Caspio fields + enrichments
- **dockets** — Court filings (N:1 to cases, N:1 to courts)
- **opinion_clusters** — Groups of opinions from a single hearing
- **opinions** — Full opinion text with search vectors
- **citations** — Case-to-case and opinion-to-opinion citation links
- **documents** — Court filings, motions, orders with RECAP integration

### Classification & Metadata
- **parties** — Litigant entities with entity resolution
- **case_parties** — Junction table (N:N cases ↔ parties with roles)
- **judges** — Judicial officers with CourtListener person IDs
- **case_judges** — Junction table (N:N cases ↔ judges with roles)
- **ai_classifications** — Multi-dimensional AI tech/legal theory/industry tags
- **secondary_sources** — News, academic articles, blog posts

### Audit & Provenance
- **audit_log** — Every data change: who, what, when, old/new values
- **provenance** — Data lineage: source system, method, confidence

## Key Design Patterns

### Soft Deletes
Cases use `is_deleted` flag instead of hard DELETEs — required for legal data preservation.

### Version Chains  
`Case.version` auto-increments on update; `superseded_by_id` links to amendment records.

### JSONB Classification
`ai_technology_types`, `legal_theories`, `industry_sectors` stored as JSONB arrays on cases for flexible multi-label classification with GIN-indexed containment queries.

### Provenance Tracking
Every record from an external source (Caspio, CourtListener, manual entry) gets a provenance record documenting source system, URL, import method, and confidence score.

### Full-Text Search
PostgreSQL `tsvector` columns with automatic trigger updates. Weighted search: caption (A) > description + keywords (B) > issues + cause of action (C) > facts (D).

## External Integrations

### CourtListener REST API v4.4
- **Auth**: Token-based (`Authorization: Token <key>`)
- **Rate limit**: 5,000 queries/hour
- **Endpoints used**: dockets, opinions, RECAP, citations, people, courts
- **anti-hallucination**: Citation verification via lookup endpoint

### eyecite
- Python library for legal citation extraction
- Handles FullCaseCitation, ShortCaseCitation, SupraCitation, IdCitation
- Maintained by the Free Law Project
