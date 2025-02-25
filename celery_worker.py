from celery import Celery
from app import app 
from models import User, ParsingResult
from utils import parse_and_update

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config.get("CELERY_RESULT_BACKEND"),
        broker=app.config.get("CELERY_BROKER_URL"),
    )
    celery.conf.update(app.config)
    return celery

app.config["CELERY_BROKER_URL"] = "redis://localhost:6379/0"
app.config["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/0"

celery = make_celery(app)

@celery.task
def parse_user_data(user_email):
    """Парсинг всіх збережених URL конкретного користувача"""
    with app.app_context():
        results = ParsingResult.query.filter_by(user_email=user_email).all()
        if not results:
            return f"No parsing data for {user_email}."

        for result in results:
            parse_and_update(user_email, result.url, result.xpath)

        return f"Parsing completed for {user_email}."

@celery.task
def parse_all_users():
    """Фонове завдання для парсингу всіх користувачів"""
    with app.app_context():
        users = User.query.all()
        for user in users:
            if ParsingResult.query.filter_by(user_email=user.email).count() > 0:
                parse_user_data.delay(user.email)  # Асинхронний запуск парсингу
       