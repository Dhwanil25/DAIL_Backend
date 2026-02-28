"""
Ingestion Tasks — Celery tasks for data import operations.

Handles asynchronous Caspio migration and CourtListener enrichment.
"""

from app.tasks.celery_app import celery_app
import structlog

logger = structlog.get_logger()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def enrich_case_from_courtlistener(self, case_id: int, docket_url: str):
    """
    Async task: Enrich a DAIL case with CourtListener data.
    Fetches docket metadata, party info, and filing details.
    """
    import asyncio
    from app.database import async_session_factory
    from app.services.ingestion_service import get_ingestion_service

    async def _run():
        service = get_ingestion_service()
        async with async_session_factory() as session:
            try:
                result = await service.enrich_case_from_courtlistener(
                    case_id, docket_url, session
                )
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                raise e

    try:
        result = asyncio.get_event_loop().run_until_complete(_run())
        logger.info(
            "CourtListener enrichment completed",
            case_id=case_id,
            result=result,
        )
        return result
    except Exception as exc:
        logger.error(
            "CourtListener enrichment failed",
            case_id=case_id,
            error=str(exc),
        )
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=1)
def bulk_import_caspio_xlsx(self, file_path: str, table_type: str):
    """
    Async task: Import data from a Caspio XLSX export file.

    Args:
        file_path: Path to the XLSX file
        table_type: 'cases', 'dockets', 'documents', or 'secondary_sources'
    """
    import asyncio
    import pandas as pd
    from app.database import async_session_factory
    from app.services.ingestion_service import get_ingestion_service

    async def _run():
        service = get_ingestion_service()
        df = pd.read_excel(file_path)

        imported = 0
        errors = 0

        async with async_session_factory() as session:
            for _, row in df.iterrows():
                try:
                    row_dict = row.to_dict()
                    # Clean NaN values
                    row_dict = {
                        k: (None if pd.isna(v) else v)
                        for k, v in row_dict.items()
                    }

                    if table_type == "cases":
                        await service.import_caspio_case(row_dict, session)
                    imported += 1
                except Exception as e:
                    errors += 1
                    logger.error(
                        "Row import failed",
                        table_type=table_type,
                        error=str(e),
                    )

            await session.commit()

        return {"imported": imported, "errors": errors, "total": len(df)}

    try:
        result = asyncio.get_event_loop().run_until_complete(_run())
        logger.info("Bulk import completed", **result)
        return result
    except Exception as exc:
        logger.error("Bulk import failed", error=str(exc))
        raise self.retry(exc=exc)
