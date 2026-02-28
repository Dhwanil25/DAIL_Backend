# DAIL Backend — Migration Guide

## Migrating from Caspio to DAIL Backend

This guide covers the complete process of migrating your existing DAIL data from Caspio Excel exports to the new PostgreSQL-based backend.

---

## Prerequisites

1. **Docker & Docker Compose** installed
2. **Python 3.12+** (for running scripts locally)
3. The 4 Caspio XLSX export files in the workspace root:
   - `Case_Table_*.xlsx`
   - `Docket_Table_*.xlsx`  
   - `Document_Table_*.xlsx`
   - `Secondary_Source_Coverage_Table_*.xlsx`
4. A CourtListener API token (optional, for enrichment)

---

## Step 1: Start the Infrastructure

```bash
# Start PostgreSQL and Redis
docker compose up -d db redis

# Wait for PostgreSQL to be ready
docker compose exec db pg_isready -U dail_user
```

## Step 2: Run Database Migrations

```bash
# Apply the schema
docker compose run --rm migrate

# Or locally:
alembic upgrade head
```

## Step 3: Seed Reference Data

```bash
# Seed federal courts
python -m scripts.seed_courts
```

This inserts 23 federal courts (SCOTUS, all circuits, key district courts).

## Step 4: Import Caspio Data

```bash
# Run the full migration
python -m scripts.migrate_caspio
```

This will:
1. Read each XLSX file using pandas
2. Map Caspio column names to the new schema
3. Create provenance records for every imported row  
4. Skip duplicate `record_number` values
5. Print import statistics

### Expected Output
```
Workspace: /path/to/DAIL_Backend
============================================================
Importing cases from: Case_Table_2026-Feb-21_1952.xlsx
  Found 450 rows
  Cases: 450 imported, 0 skipped
Importing dockets from: Docket_Table_2026-Feb-21_2003.xlsx
  Found 312 rows
  Dockets: 310 imported, 2 skipped
...
============================================================
Migration complete!
```

## Step 5: Run Classification

After importing cases, run the automated classification:

```bash
# Via Celery task
celery -A app.tasks.celery_app call app.tasks.classification_tasks.classify_all_cases

# Or start the worker and let it process
docker compose up -d celery_worker
```

This applies rule-based patterns to classify each case by:
- AI technology type (facial recognition, generative AI, etc.)
- Legal theory (due process, discrimination, etc.)
- Industry sector (healthcare, finance, etc.)

## Step 6: Enrich with CourtListener

```bash
# Set your API token
export COURTLISTENER_API_TOKEN=your_token_here

# Scan CourtListener for new AI cases
python -m scripts.import_courtlistener

# Enrich a specific case with CL data
curl -X POST http://localhost:8000/api/v1/cases/1/enrich \
  -H "X-API-Key: your-key"
```

## Step 7: Verify the Migration

```bash
# Check case counts
curl http://localhost:8000/api/v1/analytics/summary | python -m json.tool

# Test search
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "facial recognition"}'
```

---

## Field Mapping Reference

### Cases

| Caspio Column | New Field | Notes |
|---------------|-----------|-------|
| Record_Number | record_number | Preserved as-is |
| Caption | caption | — |
| Case_Slug | case_slug | — |
| Brief_Description | brief_description | — |
| Facts | facts | New field, populated from description |
| Area_of_Application | area_of_application | — |
| Issue | issue_text | Renamed |
| Cause_of_Action | cause_of_action | — |
| Algorithm_Name | algorithm_name | — |
| Algorithm_Description | algorithm_description | — |
| Class_Action | is_class_action | Cast to boolean |
| Jurisdiction_Name | jurisdiction_name | — |
| Jurisdiction_Type | jurisdiction_type | — |
| Jurisdiction_State | jurisdiction_state | — |
| Status_Disposition | status_disposition | — |
| Organizations_Involved | organizations_involved | — |
| Keywords | keywords | — |
| Lead_Case | lead_case | — |
| Related_Cases | related_cases | — |
| Notes | notes | — |
| — | ai_technology_types | NEW: Auto-classified JSONB array |
| — | legal_theories | NEW: Auto-classified JSONB array |
| — | search_vector | NEW: Auto-generated tsvector |

### Dockets

| Caspio Column | New Field |
|---------------|-----------|
| Case_Number | case_id (FK lookup by record_number) |
| Court | court_name |
| Docket_Number | docket_number |
| Link | link |

### Documents

| Caspio Column | New Field |
|---------------|-----------|
| Case_Number | case_id (FK lookup by record_number) |
| Document_Title | document_title |
| Document_Date | document_date |
| Cite_or_Reference | cite_or_reference |
| Link | link |

### Secondary Sources

| Caspio Column | New Field |
|---------------|-----------|
| Case_Number | case_id (FK lookup by record_number) |
| Secondary_Source_Title | title |
| Secondary_Source_Link | link |

---

## Rollback

If you need to rollback the migration:

```bash
# Revert the database schema
alembic downgrade base

# Or drop all tables
docker compose exec db psql -U dail_user -d dail -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

The original XLSX files are never modified.
