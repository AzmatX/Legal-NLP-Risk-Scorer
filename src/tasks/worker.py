from tasks.celery_app import celery_app


@celery_app.task(name="tasks.healthcheck")
def healthcheck() -> str:
    return "ok"
