"""Analytics / dashboard-stats endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.case import Case
from app.models.docket import Docket
from app.models.document import Document
from app.models.secondary_source import SecondarySource

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
async def analytics_summary(db: AsyncSession = Depends(get_db)):
    """Return high-level database statistics for a dashboard."""

    total_cases = (await db.execute(select(func.count(Case.id)))).scalar_one()
    total_dockets = (await db.execute(select(func.count(Docket.id)))).scalar_one()
    total_documents = (await db.execute(select(func.count(Document.id)))).scalar_one()
    total_sources = (await db.execute(select(func.count(SecondarySource.id)))).scalar_one()

    # Status breakdown
    status_sql = text("""
        SELECT coalesce(status_disposition, 'Unknown') AS status, count(*) AS count
        FROM cases GROUP BY status ORDER BY count DESC
    """)
    statuses = [dict(r) for r in (await db.execute(status_sql)).mappings().all()]

    # Jurisdiction type breakdown
    jtype_sql = text("""
        SELECT coalesce(jurisdiction_type, 'Unknown') AS jurisdiction_type, count(*) AS count
        FROM cases GROUP BY jurisdiction_type ORDER BY count DESC
    """)
    jtypes = [dict(r) for r in (await db.execute(jtype_sql)).mappings().all()]

    # Area of application breakdown
    area_sql = text("""
        SELECT coalesce(area_of_application, 'Unknown') AS area, count(*) AS count
        FROM cases GROUP BY area ORDER BY count DESC LIMIT 15
    """)
    areas = [dict(r) for r in (await db.execute(area_sql)).mappings().all()]

    # Yearly filing distribution
    yearly_sql = text("""
        SELECT extract(year FROM date_action_filed)::int AS year, count(*) AS count
        FROM cases WHERE date_action_filed IS NOT NULL
        GROUP BY year ORDER BY year
    """)
    yearly = [dict(r) for r in (await db.execute(yearly_sql)).mappings().all()]

    return {
        "totals": {
            "cases": total_cases,
            "dockets": total_dockets,
            "documents": total_documents,
            "secondary_sources": total_sources,
        },
        "status_breakdown": statuses,
        "jurisdiction_type_breakdown": jtypes,
        "area_breakdown": areas,
        "yearly_filings": yearly,
    }
