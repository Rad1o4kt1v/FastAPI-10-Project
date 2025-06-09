from celery import Celery

celery = Celery(
    __name__,
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

celery.conf.task_routes = {"app.tasks.*": {"queue": "default"}}

# 👇 ОБЯЗАТЕЛЬНО!
import app.tasks  # этот импорт регистрирует задачи
