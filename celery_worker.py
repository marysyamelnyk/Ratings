from celery import Celery
from app import app  # Імпортуємо Flask app

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config["result_backend"],
        broker=app.config["broker_url"],
        include=["tasks"],  # Включаємо модуль із задачами
    )
    celery.conf.update(app.config)
    return celery

# Конфігурація Celery
app.config["broker_url"] = "redis://localhost:6379/0"
app.config["result_backend"] = "redis://localhost:6379/0"

celery = make_celery(app)

# Оновлення розкладу для Celery Beat
from celery.schedules import crontab

celery.conf.beat_schedule = {
    "parse_users_every_5_minutes": {
        "task": "tasks.parse_all_users",  # Використовуємо правильний шлях
        "schedule": crontab(minute="*/5"),  # Запуск кожні 5 хвилин
    },
}
