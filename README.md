# LIA — Legal Intelligence Assistant

**Legal Intelligence Assistant** — A full-stack platform for tracking, classifying, and analyzing AI-related litigation. Built with **FastAPI + PostgreSQL** on the backend and **Next.js 15** on the frontend.

Migrated from the legacy Caspio platform — schema matches Caspio exports exactly. Includes optional LLM integration (OpenAI GPT-4o for search/summarisation, Google Gemini for document image extraction).

---

## Quick Start

```bash
# 1. Clone and configure
git clone https://github.com/Dhwanil25/DAIL_Backend.git
cd LIA_Backend
cp .env.example .env          # edit AI keys if desired

# 2. Start backend services (PostgreSQL + FastAPI)
docker compose up -d

# 3. Run database migrations
docker compose run --rm migrate

# 4. Seed data from Caspio Excel exports (place .xlsx files in project root)
docker compose build api      # rebuild to include xlsx files
docker compose up -d api
docker compose exec api python scripts/seed_from_excel.py

# 5. Start the frontend
cd frontend
npm install
npm run dev
```

| Service | URL |
|---------|-----|
| **Frontend Dashboard** | http://localhost:3000 |
| **REST API** | http://localhost:8000/api/v1 |
| **Interactive API Docs** | http://localhost:8000/docs |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 15 (App Router, Turbopack) |
| UI | React 19, Tailwind CSS v4, Framer Motion |
| Charts | Recharts |
| API Framework | FastAPI (Python 3.12) |
| Database | PostgreSQL 16 (tsvector, GIN indexes) |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| AI / LLM | OpenAI GPT-4o, Google Gemini (optional) |
| Deployment | Docker + Docker Compose |

---

## Database Schema (4 tables)

| Table | Rows | Description |
|-------|------|-------------|
| `cases` | 375 | AI litigation cases (35 columns incl. full-text search) |
| `dockets` | 378 | Court docket entries per case |
| `documents` | 841 | Court documents, orders, opinions |
| `secondary_sources` | 377 | News articles, academic coverage |

All child tables reference `cases.record_number` via foreign key.

---

## Project Structure

```
LIA_Backend/
├── app/                           # FastAPI backend
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Pydantic settings
│   ├── database.py                # Async SQLAlchemy engine
│   ├── models/                    # 4 SQLAlchemy ORM models
│   │   ├── case.py                # Cases (35 columns)
│   │   ├── docket.py              # Dockets (FK → cases)
│   │   ├── document.py            # Documents (FK → cases)
│   │   └── secondary_source.py
│   ├── schemas/                   # Pydantic request/response schemas
│   ├── api/v1/                    # Versioned REST endpoints
│   │   ├── cases.py               # Full CRUD + record-number lookup
│   │   ├── dockets.py             # CRUD filtered by case
│   │   ├── documents.py           # CRUD filtered by case
│   │   ├── secondary_sources.py
│   │   ├── search.py              # Full-text search (tsvector)
│   │   ├── analytics.py           # Dashboard stats
│   │   ├── ai.py                  # LLM endpoints (GPT-4o, Gemini)
│   │   └── health.py              # Liveness check
│   └── services/
│       └── ai_service.py          # GPT-4o + Gemini integration
├── frontend/                      # Next.js 15 dashboard
│   ├── app/                       # App Router pages
│   │   ├── page.tsx               # Dashboard home
│   │   ├── cases/                 # Cases list & detail
│   │   ├── dockets/               # Dockets browser
│   │   ├── documents/             # Documents browser
│   │   ├── sources/               # Secondary sources
│   │   ├── search/                # Global search (all types)
│   │   ├── analytics/             # Charts & stats
│   │   ├── ai/                    # AI assistant chat
│   │   └── help/                  # Documentation
│   ├── components/
│   │   ├── layout/                # Sidebar, topbar, command palette
│   │   └── dashboard/             # Case table, intelligence panel
│   ├── lib/                       # API client, hooks, utilities
│   └── types/                     # TypeScript interfaces
├── alembic/                       # Database migrations
│   └── versions/
│       ├── 001_caspio_schema.py
│       └── 002_add_document_field.py
├── scripts/
│   └── seed_from_excel.py         # Import Caspio XLSX → PostgreSQL
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Frontend Features

- **Dashboard** — Live stats, recent cases table, AI intelligence panel
- **Global Search** — Real-time search across all 4 data types with category tabs
- **Analytics** — Case status pie chart, yearly filing bar chart, area-of-application breakdown
- **AI Assistant** — Chat interface powered by GPT-4o for NL queries and case summarization
- **Full CRUD** — Browse, filter, and manage cases, dockets, documents, and secondary sources
- **Command Palette** — `⌘K` quick navigation across all pages

---

## API Endpoints

| Resource | Prefix | Endpoints | Description |
|----------|--------|-----------|-------------|
| Cases | `/cases` | GET, POST, PATCH, DELETE | Full CRUD, record-number lookup, pagination |
| Dockets | `/dockets` | GET, POST, PATCH, DELETE | Filter by `case_number` |
| Documents | `/documents` | GET, POST, PATCH, DELETE | Filter by `case_number` |
| Secondary Sources | `/secondary-sources` | GET, POST, PATCH, DELETE | Filter by `case_number` |
| Search | `/search` | GET | Full-text search across cases |
| Analytics | `/analytics/summary` | GET | Dashboard stats (status, jurisdiction, area breakdowns) |
| AI | `/ai/*` | POST | NL search, summarise, trends, classify, extract (requires API keys) |
| Health | `/health` | GET | Liveness check |

All endpoints are prefixed with `/api/v1`.

---

## Seeding Data

Place the 4 Caspio Excel exports in the project root:

- `Case_Table_2026-Feb-21_1952.xlsx`
- `Docket_Table_2026-Feb-21_2003.xlsx`
- `Document_Table_2026-Feb-21_2002.xlsx`
- `Secondary_Source_Coverage_Table_2026-Feb-21_2058.xlsx`

Then run:

```bash
docker compose exec api python scripts/seed_from_excel.py
```

The script clears existing data, reads all Excel sheets, maps columns to DB fields, and inserts with FK validation.

---

## Development

```bash
# Backend — run locally (requires PostgreSQL)
pip install -r requirements.txt
uvicorn app.main:app --reload

# Backend — run with Docker
docker compose up -d

# Frontend — development server
cd frontend
npm install
npm run dev
```

---

## Environment Variables

See [.env.example](.env.example) for all configuration options:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL async connection string |
| `OPENAI_API_KEY` | OpenAI API key (optional — enables AI endpoints) |
| `GEMINI_API_KEY` | Google Gemini API key (optional — enables image extraction) |

---

## License

See [LICENSE](LICENSE) for details.
