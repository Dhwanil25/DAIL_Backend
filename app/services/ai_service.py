"""
DAIL Backend - AI Service

LLM integration layer:
  • GPT-4o-mini (via OpenRouter) → natural-language search, case
                                   summarisation, trend analysis,
                                   auto-classification
  • Gemini 3 Flash Preview (direct Google API) → court-document image
                                                  extraction
"""

from __future__ import annotations

import base64
import json
import logging
from typing import Any, Optional

import google.generativeai as genai
from openai import AsyncOpenAI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# ── OpenRouter Client (for GPT-4o-mini) ──────────────────────────────
_openrouter_client: Optional[AsyncOpenAI] = None
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
GPT_MODEL = "openai/gpt-4o-mini"


def _get_openrouter() -> AsyncOpenAI:
    """Singleton AsyncOpenAI client pointed at OpenRouter."""
    global _openrouter_client
    if _openrouter_client is None:
        _openrouter_client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
        )
    return _openrouter_client


# ── Gemini Client (direct Google API) ────────────────────────────────
_gemini_configured = False
GEMINI_MODEL = "gemini-3-flash-preview"


def _ensure_gemini() -> None:
    global _gemini_configured
    if not _gemini_configured:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _gemini_configured = True


# ── Filterable case fields for GPT prompt context ────────────────────
FILTERABLE_FIELDS = [
    ("caption", "Case name / title"),
    ("area_of_application", "AI application area, e.g. 'Natural Language Processing', 'Computer Vision'"),
    ("issue_list", "Legal issues, e.g. 'Copyright', 'Privacy', 'Discrimination'"),
    ("cause_of_action_list", "Causes of action"),
    ("jurisdiction_type", "'U.S. Federal', 'U.S. State', 'International'"),
    ("status_disposition", "e.g. 'Active', 'Settled', 'Dismissed'"),
    ("organizations_involved", "Companies or organizations"),
    ("class_action_list", "Class-action status"),
    ("name_of_algorithm_list", "AI / algorithm names"),
    ("jurisdiction_name", "Specific jurisdiction"),
    ("researcher", "Researcher name"),
]

_FIELD_DESCRIPTION = "\n".join(
    f"  - {name}: {desc}" for name, desc in FILTERABLE_FIELDS
)


# =====================================================================
#  1. Natural-Language Search  (GPT-4o-mini via OpenRouter)
# =====================================================================
async def natural_language_search(
    query: str, db: AsyncSession
) -> dict[str, Any]:
    """Convert a plain-English question into SQL filters via GPT,
    execute the query, and return results with a GPT summary."""

    client = _get_openrouter()

    system_prompt = f"""You are a legal-database query assistant for the
Database of AI Litigation (DAIL).  Given a natural-language query, extract
structured search parameters.

Filterable columns in the *cases* table:
{_FIELD_DESCRIPTION}

Return **valid JSON** with exactly this shape:
{{
  "filters": {{ "column_name": "search_value", ... }},
  "keywords": ["word1", "word2"],
  "explanation": "Brief note on how you interpreted the query"
}}

Rules:
• Only include a filter when the query clearly implies it.
• Filter values will be matched with ILIKE %value%.
• keywords are extra free-text terms for full-text search.
• Do NOT invent column names outside the list above."""

    resp = await client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    parsed = json.loads(resp.choices[0].message.content)
    filters: dict = parsed.get("filters", {})
    keywords: list[str] = parsed.get("keywords", [])
    explanation: str = parsed.get("explanation", "")

    conditions: list[str] = []
    params: dict[str, Any] = {}
    valid_columns = {f[0] for f in FILTERABLE_FIELDS}

    for i, (col, val) in enumerate(filters.items()):
        if col not in valid_columns:
            continue
        param_key = f"p{i}"
        conditions.append(f"{col} ILIKE :{param_key}")
        params[param_key] = f"%{val}%"

    if keywords:
        ts_query = " | ".join(keywords)
        conditions.append("search_vector @@ to_tsquery('english', :ts)")
        params["ts"] = ts_query

    where_clause = " AND ".join(conditions) if conditions else "TRUE"
    sql = text(
        f"SELECT id, record_number, caption, area_of_application, "
        f"issue_list, status_disposition, jurisdiction_type, "
        f"organizations_involved, date_action_filed "
        f"FROM cases WHERE {where_clause} ORDER BY date_action_filed DESC NULLS LAST LIMIT 50"
    )
    rows = (await db.execute(sql, params)).mappings().all()
    cases = [dict(r) for r in rows]

    if cases:
        summary_prompt = (
            f"The user asked: \"{query}\"\n\n"
            f"The database returned {len(cases)} case(s).  Here are the first "
            f"few:\n{json.dumps(cases[:10], default=str)}\n\n"
            "Write a concise 2-4 sentence summary of these results for a legal "
            "researcher.  Do not fabricate information."
        )
        summary_resp = await client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "You are a legal research assistant."},
                {"role": "user", "content": summary_prompt},
            ],
            temperature=0.3,
        )
        summary = summary_resp.choices[0].message.content
    else:
        summary = "No cases matched the query."

    return {
        "query": query,
        "interpretation": explanation,
        "filters_applied": filters,
        "keywords": keywords,
        "total_results": len(cases),
        "cases": cases,
        "summary": summary,
    }


# =====================================================================
#  2. Case Summarisation  (GPT-4o-mini via OpenRouter)
# =====================================================================
async def summarize_case(case_data: dict[str, Any]) -> dict[str, Any]:
    """Generate a structured summary for a single case."""

    client = _get_openrouter()
    prompt = f"""Summarise this AI-litigation case for a legal researcher.

Case: {case_data.get('caption', 'N/A')}
Record #: {case_data.get('record_number', 'N/A')}
Status: {case_data.get('status_disposition', 'N/A')}
Area: {case_data.get('area_of_application', 'N/A')}
Issues: {case_data.get('issue_text', 'N/A')}
Causes of Action: {case_data.get('cause_of_action_text', 'N/A')}
Facts: {case_data.get('summary_facts_activity', 'N/A')}
Significance: {case_data.get('summary_of_significance', 'N/A')}
Organisations: {case_data.get('organizations_involved', 'N/A')}
Jurisdiction: {case_data.get('jurisdiction_name', 'N/A')} ({case_data.get('jurisdiction_type', 'N/A')})
Filed: {case_data.get('date_action_filed', 'N/A')}
Class Action: {case_data.get('class_action', 'N/A')}
Algorithm: {case_data.get('name_of_algorithm_text', 'N/A')}

Provide:
1. **Overview** (2-3 sentences)
2. **Key Legal Issues**
3. **AI Technology Involved**
4. **Current Status & Implications**
5. **Significance for AI Law**

Be concise and accurate.  Only use information provided above."""

    resp = await client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": "You are a legal research assistant specialising in AI litigation."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    return {
        "case_id": case_data.get("id"),
        "record_number": case_data.get("record_number"),
        "caption": case_data.get("caption"),
        "summary": resp.choices[0].message.content,
    }


# =====================================================================
#  3. Trend Analysis  (GPT-4o-mini via OpenRouter)
# =====================================================================
async def analyze_trends(
    question: str, db: AsyncSession
) -> dict[str, Any]:
    """Fetch aggregate data and ask GPT to identify trends."""

    client = _get_openrouter()

    stats_sql = text("""
        SELECT
            count(*) AS total,
            count(*) FILTER (WHERE status_disposition ILIKE '%%active%%') AS active,
            count(*) FILTER (WHERE jurisdiction_type ILIKE '%%federal%%') AS federal,
            count(*) FILTER (WHERE jurisdiction_type ILIKE '%%state%%')   AS state,
            count(*) FILTER (WHERE class_action_list IS NOT NULL
                             AND class_action_list != '')               AS class_actions,
            min(date_action_filed) AS earliest_filing,
            max(date_action_filed) AS latest_filing
        FROM cases
    """)
    stats = dict((await db.execute(stats_sql)).mappings().first())

    area_sql = text("""
        SELECT area_of_application, count(*) AS cnt
        FROM cases
        WHERE area_of_application IS NOT NULL AND area_of_application != ''
        GROUP BY area_of_application ORDER BY cnt DESC LIMIT 15
    """)
    areas = [dict(r) for r in (await db.execute(area_sql)).mappings().all()]

    issue_sql = text("""
        SELECT issue_list, count(*) AS cnt
        FROM cases
        WHERE issue_list IS NOT NULL AND issue_list != ''
        GROUP BY issue_list ORDER BY cnt DESC LIMIT 15
    """)
    issues = [dict(r) for r in (await db.execute(issue_sql)).mappings().all()]

    year_sql = text("""
        SELECT EXTRACT(YEAR FROM date_action_filed)::int AS year, count(*) AS cnt
        FROM cases
        WHERE date_action_filed IS NOT NULL
        GROUP BY year ORDER BY year
    """)
    yearly = [dict(r) for r in (await db.execute(year_sql)).mappings().all()]

    context_blob = json.dumps(
        {"stats": stats, "areas": areas, "issues": issues, "yearly": yearly},
        default=str,
    )
    prompt = (
        f"The user asked: \"{question}\"\n\n"
        f"Here is aggregated data from the DAIL database:\n{context_blob}\n\n"
        "Based on this data, provide an insightful analysis answering the "
        "user's question.  Include specific numbers.  Be concise (3-6 "
        "paragraphs)."
    )
    resp = await client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": "You are a legal analytics expert specialising in AI litigation trends."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )
    return {
        "question": question,
        "analysis": resp.choices[0].message.content,
        "data": {
            "stats": stats,
            "top_areas": areas,
            "top_issues": issues,
            "yearly_filings": yearly,
        },
    }


# =====================================================================
#  4. Auto-Classification  (GPT-4o-mini via OpenRouter)
# =====================================================================
async def classify_case(case_data: dict[str, Any]) -> dict[str, Any]:
    """Given partial case data, suggest appropriate list-field values."""

    client = _get_openrouter()
    prompt = f"""You are a legal classifier for the Database of AI Litigation.
Given the case details below, suggest the best values for each classification
field.

Case: {case_data.get('caption', '')}
Description: {case_data.get('brief_description', '')}
Facts: {case_data.get('summary_facts_activity', '')}
Organisations: {case_data.get('organizations_involved', '')}

Return **valid JSON** with these keys (use null if uncertain):
{{
  "area_of_application": "suggested value",
  "issue_list": "suggested value",
  "cause_of_action_list": "suggested value",
  "name_of_algorithm_list": "suggested value",
  "class_action_list": "Yes / No / null",
  "jurisdiction_type": "U.S. Federal / U.S. State / International / null"
}}"""

    resp = await client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": "You are a legal data classification assistant."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    suggestions = json.loads(resp.choices[0].message.content)
    return {"case_input": case_data, "suggestions": suggestions}


# =====================================================================
#  5. Document Image Extraction  (Gemini 3 Flash Preview — direct API)
# =====================================================================
async def extract_document_from_image(
    image_url: str,
    mime_type: str = "image/png",
) -> dict[str, Any]:
    """Use Google Gemini 3 Flash Preview to extract structured text
    from a court-document image (scan / screenshot)."""

    import httpx

    _ensure_gemini()
    model = genai.GenerativeModel(GEMINI_MODEL)

    async with httpx.AsyncClient(follow_redirects=True) as http:
        img_resp = await http.get(image_url, timeout=30)
        img_resp.raise_for_status()
        image_bytes = img_resp.content

    prompt = """Extract all text from the following court document image.
Then return valid JSON with these keys:
{
  "raw_text": "full extracted text",
  "case_name": "if identifiable",
  "court": "if identifiable",
  "date": "if identifiable (YYYY-MM-DD)",
  "docket_number": "if identifiable",
  "summary": "1-2 sentence summary of the document"
}
If a field is not identifiable, set it to null."""

    response = model.generate_content(
        [
            prompt,
            {"mime_type": mime_type, "data": image_bytes},
        ]
    )
    raw = response.text

    try:
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0]
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0]
        result = json.loads(raw)
    except (json.JSONDecodeError, IndexError):
        result = {"raw_text": raw, "parse_error": "Could not parse structured fields"}

    return result
