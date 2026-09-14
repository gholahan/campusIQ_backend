# import asyncio
import logging
import uuid

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

import app.db.base  # noqa: F401
from app.core.config import DATABASE_URL
from app.features.ai.rag.ingestion import process_pdf

# from app.core.celery import celery_app  # Celery removed — using FastAPI BackgroundTask


logger = logging.getLogger(__name__)


# Celery task replaced — now a plain async function for FastAPI BackgroundTask
async def upload_document(
    document_id: str,
    file_url: str,
) -> None:

    try:
        await run_process_pdf(
            document_id=document_id,
            file_url=file_url,
        )

    except Exception:
        logger.exception(
            "[%s] Background task failed",
            document_id,
        )
        raise


async def run_process_pdf(
    document_id: str,
    file_url: str,
) -> None:

    logger.info(
        "[%s] Creating database engine",
        document_id,
    )

    engine = create_async_engine(
        DATABASE_URL,
        connect_args={
            "statement_cache_size": 0,
        },
    )

    try:
        async with AsyncSession(
            engine,
            expire_on_commit=False,
        ) as session:

            await process_pdf(
                file_url=file_url,
                document_id=uuid.UUID(document_id),
                session=session,
            )

    except Exception:
        logger.exception(
            "[%s] PDF processing failed, marking document as failed",
            document_id,
        )
        # Re-raise so upload_document can log, but the ingestion layer already
        # called mark_document_failed — we just ensure the exception propagates
        raise
    finally:
        await engine.dispose()