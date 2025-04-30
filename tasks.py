from celery import shared_task
from app import app
from models import User, ParsingResult
from utils import parse_and_update

@shared_task
def parse_user_data(user_email):
    """Парсинг всіх збережених URL конкретного користувача"""
    with app.app_context():
        results = ParsingResult.query.filter_by(user_email=user_email).all()
        if not results:
            return f"No parsing data for {user_email}."

        for result in results:
            print(f"Starting parsing for {user_email} with URL: {result.url}")
            parse_and_update(user_email, result.url, result.xpath)

        return f"Parsing completed for {user_email}."

@shared_task
def parse_all_users():
    """Фонове завдання для парсингу всіх користувачів"""
    with app.app_context():
        users = User.query.all()
        for user in users:
            if ParsingResult.query.filter_by(user_email=user.email).count() > 0:
                parse_user_data.delay(user.email)  # Асинхронний запуск парсингу
