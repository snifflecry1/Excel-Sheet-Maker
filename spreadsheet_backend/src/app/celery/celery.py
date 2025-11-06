from celery import Celery
import os

def make_celery():
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

    celery = Celery(
        'spreadsheet_tasks',
        broker=redis_url,
        backend=redis_url,
        include=['app.celery.tasks']  # adjust path to your tasks file
    ) # type: ignore

    celery.conf.update(
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        timezone='UTC',
        enable_utc=True,
    )

    return celery

celery_app = make_celery()
