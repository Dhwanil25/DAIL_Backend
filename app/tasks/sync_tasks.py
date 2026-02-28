"""
Sync Tasks — periodic Celery tasks for CourtListener sync and maintenance.
"""

from app.tasks.celery_app import celery_app
import structlog

logger = structlog.get_logger()

# Keywords used to detect AI-related litigation on CourtListener
AI_SEARCH_KEYWORDS = [
    "artificial intelligence",
    "machine learning",
    "algorithm discrimination",
    "ChatGPT",
    "generative AI",
    "facial recognition",
    "autonomous vehicle",
    "deepfake",
    "AI bias",
    "algorithmic",
]


@celery_app.task
def poll_courtlistener_alerts():
    """
    Periodic task: Check CourtListener for new AI-related filings.
    Runs hourly via Celery Beat.
    """
    import asyncio
    from app.services.courtlistener import get_courtlistener_client

    async def _run():
        client = get_courtlistener_client()
        new_cases = []

        for keyword in AI_SEARCH_KEYWORDS:
            try:
                results = await client.search_dockets(
                    query=keyword,
                    date_filed_after="2024-01-01",
                )
                hits = results.get("results", [])
                new_cases.extend(hits)
                logger.info(
                    "CourtListener search",
                    keyword=keyword,
                    results=len(hits),
                )
            except Exception as e:
                logger.error(
                    "CourtListener search failed",
                    keyword=keyword,
                    error=str(e),
                )

        return {"total_candidates": len(new_cases)}

    try:
        result = asyncio.get_event_loop().run_until_complete(_run())
        logger.info("CourtListener polling completed", **result)
        return result
    except Exception as exc:
        logger.error("CourtListener polling failed", error=str(exc))
        return {"error": str(exc)}


@celery_app.task
def refresh_search_vectors():
    """
    Periodic task: Update PostgreSQL full-text search vectors for all cases.
    Runs daily via Celery Beat.
    """
    import asyncio
    from app.database import async_session_factory
    from app.services.search_service import get_search_service

    async def _run():
        service = get_search_service()
        async with async_session_factory() as session:
            count = await service.update_all_case_vectors(session)
            await session.commit()
            return {"vectors_updated": count}

    try:
        result = asyncio.get_event_loop().run_until_complete(_run())
        logger.info("Search vectors refreshed", **result)
        return result
    except Exception as exc:
        logger.error("Search vector refresh failed", error=str(exc))
        return {"error": str(exc)}
