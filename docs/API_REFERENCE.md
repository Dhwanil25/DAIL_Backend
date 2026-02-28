# DAIL Backend — API Reference

Base URL: `http://localhost:8000/api/v1`

All endpoints return JSON. Pagination uses `?page=1&page_size=20` query params.

---

## Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Database connectivity check |

---

## Cases

| Method | Path | Description |
|--------|------|-------------|
| GET | `/cases` | List cases (filterable) |
| POST | `/cases` | Create a new case |
| GET | `/cases/{id}` | Get case with all relationships |
| PATCH | `/cases/{id}` | Partial update |
| DELETE | `/cases/{id}` | Soft delete |
| GET | `/cases/record/{record_number}` | Lookup by Caspio record number |
| GET | `/cases/{id}/dockets` | List dockets for a case |
| GET | `/cases/{id}/documents` | List documents for a case |
| GET | `/cases/{id}/secondary-sources` | List secondary sources for a case |

### Case List Filters
| Parameter | Type | Example |
|-----------|------|---------|
| `status` | string | `pending`, `settled`, `dismissed` |
| `jurisdiction` | string | `federal` |
| `area_of_application` | string | `Employment` |
| `keyword` | string | Free text search |
| `is_class_action` | boolean | `true` |
| `sort_by` | string | `filed_date`, `caption`, `created_at` |
| `sort_order` | string | `asc`, `desc` |

---

## Courts

| Method | Path | Description |
|--------|------|-------------|
| GET | `/courts` | List courts (filterable by state/jurisdiction) |
| POST | `/courts` | Create court |
| GET | `/courts/{id}` | Get court details |
| PATCH | `/courts/{id}` | Update court |

---

## Dockets

| Method | Path | Description |
|--------|------|-------------|
| GET | `/dockets` | List all dockets |
| POST | `/dockets` | Create docket |
| GET | `/dockets/{id}` | Get docket |
| PATCH | `/dockets/{id}` | Update docket |

---

## Opinions

| Method | Path | Description |
|--------|------|-------------|
| GET | `/opinions/clusters` | List opinion clusters |
| POST | `/opinions/clusters` | Create cluster |
| GET | `/opinions/clusters/{id}` | Get cluster with opinions |
| POST | `/opinions` | Create opinion |
| GET | `/opinions/{id}` | Get opinion |

---

## Citations

| Method | Path | Description |
|--------|------|-------------|
| GET | `/citations` | List citations |
| POST | `/citations` | Create citation |
| GET | `/citations/{id}` | Get citation |
| GET | `/citations/case/{id}/citing` | Cases that cite this case |
| GET | `/citations/case/{id}/cited-by` | Cases cited by this case |

---

## Parties

| Method | Path | Description |
|--------|------|-------------|
| GET | `/parties` | List parties |
| POST | `/parties` | Create party |
| GET | `/parties/{id}` | Get party |
| POST | `/parties/case-party` | Link party to case with role |

---

## Judges

| Method | Path | Description |
|--------|------|-------------|
| GET | `/judges` | List judges |
| POST | `/judges` | Create judge |
| GET | `/judges/{id}` | Get judge |

---

## Documents

| Method | Path | Description |
|--------|------|-------------|
| GET | `/documents` | List documents |
| POST | `/documents` | Create document |
| GET | `/documents/{id}` | Get document |
| PATCH | `/documents/{id}` | Update document |

---

## Secondary Sources

| Method | Path | Description |
|--------|------|-------------|
| GET | `/secondary-sources` | List sources |
| POST | `/secondary-sources` | Create source |
| GET | `/secondary-sources/{id}` | Get source |
| PATCH | `/secondary-sources/{id}` | Update source |

---

## Search

| Method | Path | Description |
|--------|------|-------------|
| POST | `/search` | Full-text search across cases |

### Search Request Body
```json
{
  "query": "facial recognition",
  "ai_technology_types": ["facial_recognition"],
  "legal_theories": ["constitutional_rights"],
  "industry_sectors": ["law_enforcement"],
  "date_filed_after": "2020-01-01",
  "date_filed_before": "2025-12-31",
  "jurisdiction_type": "federal",
  "status": "pending",
  "page": 1,
  "page_size": 20,
  "sort_by": "relevance"
}
```

---

## Analytics

| Method | Path | Description |
|--------|------|-------------|
| GET | `/analytics/summary` | Dashboard statistics |

### Response includes:
- `total_cases`, `total_dockets`, `total_documents`
- `status_breakdown` — count per case status
- `jurisdiction_breakdown` — count per jurisdiction type
- `area_breakdown` — count per area of application
- `ai_technology_breakdown` — count per AI tech type
- `legal_theory_breakdown` — count per legal theory
- `year_breakdown` — cases filed per year
- `recent_cases` — last 10 created
- `most_active_jurisdictions` — top jurisdictions list

---

## Authentication

Pass an API key via the `X-API-Key` header. Most read endpoints are public; write endpoints may require a key depending on configuration.

## Rate Limiting

- **Per minute**: 60 requests (default)
- **Per hour**: 1,000 requests (default)
- Rate limit headers included in every response: `X-RateLimit-Limit`, `X-RateLimit-Remaining`
