"""
Search Service — abstraction layer over PostgreSQL full-text search.

Designed to be swappable with Elasticsearch when scale demands it.
Currently uses PostgreSQL tsvector/tsquery with GIN indexes.
"""

from typing import Optional

from sqlalchemy import text, func
from sqlalchemy.ext.asyncio import AsyncSession

import structlog

logger = structlog.get_logger()


class SearchService:
    """PostgreSQL full-text search service for DAIL."""

    @staticmethod
    async def update_search_vector(
        db: AsyncSession,
        table: str,
        record_id: int,
        text_fields: list[str],
        weights: Optional[dict[str, str]] = None,
    ) -> None:
        """
        Update the tsvector search_vector column for a record.

        Args:
            db: Database session
            table: Table name
            record_id: Primary key of the record
            text_fields: Fields to include in the search vector
            weights: Optional weight mapping: field -> 'A'|'B'|'C'|'D'
                     A = highest weight (4x), D = default (1x)
        """
        if not weights:
            weights = {}

        # Build tsvector expression
        parts = []
        for field in text_fields:
            weight = weights.get(field, "D")
            parts.append(
                f"setweight(to_tsvector('english', COALESCE({field}, '')), '{weight}')"
            )

        vector_expr = " || ".join(parts)

        query = text(f"""
            UPDATE {table}
            SET search_vector = {vector_expr}
            WHERE id = :record_id
        """)

        await db.execute(query, {"record_id": record_id})

    @staticmethod
    async def update_all_case_vectors(db: AsyncSession) -> int:
        """
        Bulk update search vectors for all cases.
        Called during initial migration or periodic maintenance.

        Returns the number of cases updated.
        """
        query = text("""
            UPDATE cases SET search_vector =
                setweight(to_tsvector('english', COALESCE(caption, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(brief_description, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(summary_of_significance, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(issue_text, '')), 'C') ||
                setweight(to_tsvector('english', COALESCE(cause_of_action, '')), 'C') ||
                setweight(to_tsvector('english', COALESCE(keyword, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(algorithm_name, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(area_of_application, '')), 'B') ||
                setweight(to_tsvector('english', COALESCE(summary_facts, '')), 'D') ||
                setweight(to_tsvector('english', COALESCE(organizations_involved, '')), 'C')
            WHERE is_deleted = FALSE
        """)

        result = await db.execute(query)
        count = result.rowcount
        logger.info("Updated search vectors", cases_updated=count)
        return count

    @staticmethod
    async def search_cases_fts(
        db: AsyncSession,
        query_text: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict]:
        """
        Full-text search with ts_rank scoring.
        Returns cases ranked by relevance.
        """
        query = text("""
            SELECT
                id,
                caption,
                brief_description,
                date_action_filed,
                status,
                jurisdiction_filed,
                area_of_application,
                ts_rank(search_vector, plainto_tsquery('english', :query)) AS rank
            FROM cases
            WHERE
                is_deleted = FALSE
                AND search_vector @@ plainto_tsquery('english', :query)
            ORDER BY rank DESC
            LIMIT :limit OFFSET :offset
        """)

        result = await db.execute(
            query, {"query": query_text, "limit": limit, "offset": offset}
        )

        return [
            {
                "id": row[0],
                "caption": row[1],
                "brief_description": row[2],
                "date_action_filed": str(row[3]) if row[3] else None,
                "status": row[4],
                "jurisdiction_filed": row[5],
                "area_of_application": row[6],
                "rank": float(row[7]),
            }
            for row in result.all()
        ]


# ── Singleton ────────────────────────────────────────────────────────────
_service: Optional[SearchService] = None


def get_search_service() -> SearchService:
    global _service
    if _service is None:
        _service = SearchService()
    return _service
