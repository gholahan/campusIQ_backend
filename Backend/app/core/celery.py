# Celery removed — replaced with FastAPI BackgroundTask
# from celery import Celery
# from app.core.config import REDIS_URL
# import app.db.base  # noqa: F401 — must run before any model is touched

# celery_app = Celery(
#     "leadgen",
#     broker=REDIS_URL,
#     backend=REDIS_URL,
# )

# celery_app.conf.update(
#     task_serializer="json",
#     accept_content=["json"],
#     result_serializer="json",
#     imports=(
#         "app.features.ai.rag.task",
#     ),
# )

celery_app = None  # Placeholder for backward compatibility