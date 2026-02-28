"""
Analytics API — database-wide statistics and breakdowns.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.case import Case
from app.models.court import Court
from app.models.docket import Docket
from app.models.document import Document
from app.models.opinion import OpinionCluster
from app.models.citation import Citation
from app.models.party import Party
from app.models.ai_classification import AIClassification
from app.schemas.search import AnalyticsSummary

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(db: AsyncSession = Depends(get_db)):
    """
    Get comprehensive database statistics: totals, breakdowns by status,
    jurisdiction, AI technology type, legal theory, and filing year.
    """
    # ── Totals ───────────────────────────────────────────────────────
    total_cases = (await db.execute(
        select(func.count()).select_from(Case).where(Case.is_deleted == False)  # noqa: E712
    )).scalar_one()

    total_documents = (await db.execute(
        select(func.count()).select_from(Document)
    )).scalar_one()

    total_opinions = (await db.execute(
        select(func.count()).select_from(OpinionCluster)
    )).scalar_one()

    total_citations = (await db.execute(
        select(func.count()).select_from(Citation)
    )).scalar_one()

    total_parties = (await db.execute(
        select(func.count()).select_from(Party).where(Party.is_alias == False)  # noqa: E712
    )).scalar_one()

    total_courts = (await db.execute(
        select(func.count()).select_from(Court)
    )).scalar_one()

    # ── Cases by Status ──────────────────────────────────────────────
    status_result = await db.execute(
        select(Case.status_disposition, func.count())
        .where(Case.is_deleted == False)  # noqa: E712
        .group_by(Case.status_disposition)
    )
    cases_by_status = {
        str(row[0]) if row[0] else "unknown": row[1]
        for row in status_result.all()
    }

    # ── Cases by Jurisdiction Type ───────────────────────────────────
    jt_result = await db.execute(
        select(Case.jurisdiction_type, func.count())
        .where(Case.is_deleted == False, Case.jurisdiction_type.isnot(None))  # noqa: E712
        .group_by(Case.jurisdiction_type)
    )
    cases_by_jurisdiction_type = {row[0]: row[1] for row in jt_result.all()}

    # ── Cases by Area of Application ─────────────────────────────────
    area_result = await db.execute(
        select(Case.area_of_application, func.count())
        .where(Case.is_deleted == False, Case.area_of_application.isnot(None))  # noqa: E712
        .group_by(Case.area_of_application)
        .order_by(func.count().desc())
        .limit(20)
    )
    cases_by_area_of_application = {row[0]: row[1] for row in area_result.all()}

    # ── Cases by AI Technology Type (from classifications) ───────────
    tech_result = await db.execute(
        select(AIClassification.ai_technology_type, func.count())
        .where(AIClassification.ai_technology_type.isnot(None))
        .group_by(AIClassification.ai_technology_type)
        .order_by(func.count().desc())
    )
    cases_by_ai_technology_type = {
        str(row[0]) if row[0] else "other": row[1]
        for row in tech_result.all()
    }

    # ── Cases by Legal Theory (from classifications) ─────────────────
    theory_result = await db.execute(
        select(AIClassification.legal_theory, func.count())
        .where(AIClassification.legal_theory.isnot(None))
        .group_by(AIClassification.legal_theory)
        .order_by(func.count().desc())
    )
    cases_by_legal_theory = {
        str(row[0]) if row[0] else "other": row[1]
        for row in theory_result.all()
    }

    # ── Cases by Filing Year ─────────────────────────────────────────
    year_result = await db.execute(
        select(
            extract("year", Case.filed_date).label("year"),
            func.count(),
        )
        .where(Case.is_deleted == False, Case.filed_date.isnot(None))  # noqa: E712
        .group_by("year")
        .order_by("year")
    )
    cases_by_year = {
        str(int(row[0])): row[1]
        for row in year_result.all()
        if row[0] is not None
    }

    # ── Recent Cases ─────────────────────────────────────────────────
    recent_result = await db.execute(
        select(Case.id, Case.caption, Case.filed_date, Case.status_disposition)
        .where(Case.is_deleted == False)  # noqa: E712
        .order_by(Case.created_at.desc())
        .limit(10)
    )
    recent_cases = [
        {
            "id": row[0],
            "caption": row[1],
            "date_filed": str(row[2]) if row[2] else None,
            "status": str(row[3]) if row[3] else None,
        }
        for row in recent_result.all()
    ]

    # ── Most Active Jurisdictions ────────────────────────────────────
    jurisdiction_result = await db.execute(
        select(Case.jurisdiction_name, func.count().label("count"))
        .where(Case.is_deleted == False, Case.jurisdiction_name.isnot(None))  # noqa: E712
        .group_by(Case.jurisdiction_name)
        .order_by(func.count().desc())
        .limit(10)
    )
    most_active_jurisdictions = [
        {"jurisdiction": row[0], "count": row[1]}
        for row in jurisdiction_result.all()
    ]

    return AnalyticsSummary(
        total_cases=total_cases,
        total_documents=total_documents,
        total_opinions=total_opinions,
        total_citations=total_citations,
        total_parties=total_parties,
        total_courts=total_courts,
        cases_by_status=cases_by_status,
        cases_by_jurisdiction_type=cases_by_jurisdiction_type,
        cases_by_area_of_application=cases_by_area_of_application,
        cases_by_ai_technology_type=cases_by_ai_technology_type,
        cases_by_legal_theory=cases_by_legal_theory,
        cases_by_year=cases_by_year,
        recent_cases=recent_cases,
        most_active_jurisdictions=most_active_jurisdictions,
    )
