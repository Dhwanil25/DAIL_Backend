"""
Classification Tasks — Celery tasks for automated case classification.
"""

from app.tasks.celery_app import celery_app
import structlog

logger = structlog.get_logger()


@celery_app.task(bind=True, max_retries=2)
def classify_case(self, case_id: int):
    """
    Async task: Run classification pipeline on a single case.
    Applies rule-based patterns and stores results.
    """
    import asyncio
    from app.database import async_session_factory
    from app.models.case import Case
    from app.models.ai_classification import AIClassification
    from app.services.classification_service import get_classification_service
    from sqlalchemy import select

    async def _run():
        classifier = get_classification_service()

        async with async_session_factory() as session:
            result = await session.execute(select(Case).where(Case.id == case_id))
            case = result.scalar_one_or_none()
            if not case:
                return {"status": "error", "message": f"Case {case_id} not found"}

            # Run classification
            classification = classifier.classify_case(
                caption=case.caption,
                description=case.brief_description or "",
                issues=case.issue_text or "",
                cause_of_action=case.cause_of_action or "",
            )

            # Update JSONB fields on the case
            case.ai_technology_types = classification["ai_technology_types"]
            case.legal_theories = classification["legal_theories"]
            case.industry_sectors = classification["industry_sectors"]

            # Store detailed classification records
            for tech in classification["ai_technology_types"]:
                ai_class = AIClassification(
                    case_id=case_id,
                    ai_technology_type=tech,
                    classification_source="rule_based",
                    confidence_score=classification["confidence_score"],
                    classified_by="rule_engine",
                )
                session.add(ai_class)

            for theory in classification["legal_theories"]:
                ai_class = AIClassification(
                    case_id=case_id,
                    legal_theory=theory,
                    classification_source="rule_based",
                    confidence_score=classification["confidence_score"],
                    classified_by="rule_engine",
                )
                session.add(ai_class)

            await session.commit()
            return {"status": "success", "classification": classification}

    try:
        result = asyncio.get_event_loop().run_until_complete(_run())
        logger.info("Case classified", case_id=case_id, result=result)
        return result
    except Exception as exc:
        logger.error("Classification failed", case_id=case_id, error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task
def classify_all_cases():
    """Classify all unclassified cases in the database."""
    import asyncio
    from app.database import async_session_factory
    from app.models.case import Case
    from sqlalchemy import select

    async def _run():
        async with async_session_factory() as session:
            result = await session.execute(
                select(Case.id).where(
                    Case.is_deleted == False,  # noqa: E712
                    Case.ai_technology_types == None,  # noqa: E711
                )
            )
            case_ids = [row[0] for row in result.all()]

        for cid in case_ids:
            classify_case.delay(cid)

        return {"queued": len(case_ids)}

    result = asyncio.get_event_loop().run_until_complete(_run())
    logger.info("Queued classification for unclassified cases", **result)
    return result
