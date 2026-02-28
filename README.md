# DAIL Backend

**Database of AI Litigation** — A production-grade REST API for tracking, classifying, and analyzing AI-related litigation in the United States.

Built with **FastAPI + PostgreSQL + Redis + Celery**, migrating from the legacy Caspio platform with full CourtListener integration.

---

## Quick Start

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env with your database credentials and CourtListener API token

# 2. Start all services with Docker
docker compose up -d

# 3. Run database migrations
docker compose run --rm migrate

# 4. Seed reference data
docker compose exec api python -m scripts.seed_courts

# 5. Import existing Caspio data
docker compose exec api python -m scripts.migrate_caspio
```

The API is now available at **http://localhost:8000**  
Interactive docs at **http://localhost:8000/docs**

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| API Framework | FastAPI (Python 3.12) |
| Database | PostgreSQL 16 (JSONB, tsvector, GIN indexes) |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Cache / Rate Limit | Redis 7 |
| Task Queue | Celery |
| Citation Parsing | eyecite |
| External Data | CourtListener REST API v4.4 |
| Deployment | Docker + Docker Compose |

---

## Project Structure

```
DAIL_Backend/
├── app/
│   ├── main.py              # FastAPI application factory
│   ├── config.py             # Pydantic settings
│   ├── database.py           # Async SQLAlchemy engine
│   ├── models/               # 13 SQLAlchemy models
│   ├── schemas/              # Pydantic request/response schemas
│   ├── api/v1/               # Versioned REST endpoints
│   ├── services/             # Business logic layer
│   │   ├── courtlistener.py  # CourtListener API client
│   │   ├── citation_service.py
│   │   ├── classification_service.py
│   │   ├── entity_resolution.py
│   │   ├── search_service.py
│   │   └── ingestion_service.py
│   ├── tasks/                # Celery async tasks
│   ├── middleware/            # Rate limiting, audit logging
│   └── utils/                # Pagination, validators
├── alembic/                  # Database migrations
├── scripts/                  # Data import & seeding scripts
├── tests/                    # pytest + httpx async test suite
├── docs/                     # Architecture, API ref, migration guide
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## API Endpoints

| Resource | Endpoints | Description |
|----------|-----------|-------------|
| Cases | 9 | Full CRUD + filters, soft delete, record number lookup |
| Courts | 4 | Court definitions linked to CourtListener |
| Dockets | 4 | Court filings per case |
| Opinions | 5 | Cluster + individual opinion CRUD |
| Citations | 5 | Citation links + citing/cited-by queries |
| Parties | 4 | Litigant entities with role assignment |
| Judges | 3 | Judicial officers |
| Documents | 4 | Court documents with RECAP integration |
| Secondary Sources | 4 | News, academic articles |
| Search | 1 | Full-text + faceted search |
| Analytics | 1 | Dashboard statistics |
| Health | 1 | Liveness check |

Full API reference: [docs/API_REFERENCE.md](docs/API_REFERENCE.md)

---

## Key Features

- **Caspio Migration**: Import existing XLSX exports preserving all fields + provenance
- **CourtListener Integration**: Async API client with rate limiting, enrichment pipeline
- **Full-Text Search**: PostgreSQL tsvector with weighted fields and GIN indexes
- **AI Classification**: Rule-based detection of 15 AI tech types, 11 legal theories
- **Citation Extraction**: eyecite + CourtListener verification
- **Entity Resolution**: Jaro-Winkler name matching for parties and judges
- **Audit Trail**: Every change logged with old/new values, IP, user, timestamp
- **Data Provenance**: Source tracking for every record (Caspio, CourtListener, manual)

---

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (requires PostgreSQL and Redis)
uvicorn app.main:app --reload

# Run tests
pytest tests/ -v

# Run linting
ruff check app/
mypy app/
```

---

## Documentation

- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md) — Phased build roadmap
- [Architecture](docs/ARCHITECTURE.md) — System design and data model
- [API Reference](docs/API_REFERENCE.md) — Complete endpoint documentation
- [Migration Guide](docs/MIGRATION_GUIDE.md) — Caspio → PostgreSQL migration steps

---

## License

See [LICENSE](LICENSE) for details.
