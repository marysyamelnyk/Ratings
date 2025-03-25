from bot_config import bot
import logging
from app import db, User, app
from urllib.parse import unquote

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    first_name = message.chat.first_name or "User"
    
    text = message.text.strip()

    # Перевіряємо, чи є параметр start=subscribe_
    if text.startswith("/start subscribe_"):
        encoded_email = text.replace("/start subscribe_", "").strip()
        email = unquote(encoded_email)  # Декодуємо email

        with app.app_context():
            user = User.query.filter_by(email=email).first()
            if user:
                user.telegram_id = str(chat_id)
                db.session.commit()
                bot.reply_to(message, f"✅ Your Telegram successfully connected with {email}!")
                print(f"✅ Connected chat_id: {chat_id} with {email}")
            else:
                bot.reply_to(message, "❌ This email was not found. Please check your data.")

    else:
        bot.reply_to(message, f"Hello, {first_name}! Enter your email:")

def send_telegram_message(user_email, text):
    from app import User, app

    with app.app_context():
        try:
            user = User.query.filter_by(email=user_email).first()
            if user and user.telegram_id:
                bot.send_message(user.telegram_id, text)
                return True
            else:
                logging.warning(f"User with an email {user_email} is not found or doesn't have Telegram ID")
                return False
        except Exception as e:
            logging.error(f"Error during sending the message: {e}")
            return False


if __name__ == "__main__":
    print("Bot is running...")
    bot.polling(none_stop=True)