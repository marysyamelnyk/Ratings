from app.models import db, ParsingResult
from app.platform_class import Platform
from telega_bot.telegram_bot import send_telegram_message
import re
from datetime import datetime, timezone
import pytz

DEFAULT_TIMEZONE = "Europe/Kyiv"  # Змініть на потрібний часовий пояс

def parse_and_update(user_email, url, xpath, user_timezone=None):    
    platform = Platform(url=url, xpath=xpath)
    result = platform.parser()
    print(f"Raw result from platform.parser(): {result}")  # Debugging print

    pattern = r"\['(.*?)'\]"
    match = re.search(pattern, result)

    if not match:
        raise ValueError("No matching data found in the result")

    result = match.group(1)
    print(f"Parsed result: {result}")  # Debugging print

    existing_result = ParsingResult.query.filter_by(user_email=user_email, url=url).first()

    # Отримуємо поточний UTC час
    current_utc_time = datetime.now(timezone.utc)

    if existing_result:
        existing_result.timestamp = current_utc_time  # ✅ Завжди оновлюємо час

        if existing_result.result == result:  # ✅ Якщо результат не змінився
            db.session.commit()  # ✅ Фіксуємо зміну часу
            return {
                "url": url,
                "xpath": xpath,
                "result": result,
                "timestamp": convert_utc_to_user_time(current_utc_time, user_timezone),
                "message": "Timestamp updated, no changes in result"
            }

        # ✅ Якщо результат змінився, оновлюємо також його
        existing_result.result = result
        send_telegram_message(user_email, f" Рейтинг на {url} змінився: {result}")
        db.session.commit()

        return {
            "url": url,
            "xpath": xpath,
            "result": result,
            "timestamp": convert_utc_to_user_time(current_utc_time, user_timezone),
            "message": "Result updated"
        }

    # ✅ Якщо такого запису немає, створюємо новий
    parsing_result = ParsingResult(user_email=user_email, url=url, xpath=xpath, result=result)
    db.session.add(parsing_result)
    db.session.commit()

    return {
        "url": url,
        "xpath": xpath,
        "result": result,
        "timestamp": convert_utc_to_user_time(current_utc_time, user_timezone),
        "message": "New result added"
    }

def convert_utc_to_user_time(utc_time, user_timezone):
    if not user_timezone:
        user_timezone = DEFAULT_TIMEZONE

    local_tz = pytz.timezone(user_timezone)
    return utc_time.astimezone(local_tz).strftime("%Y-%m-%d %H:%M:%S")    