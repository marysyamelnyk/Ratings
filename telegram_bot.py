import telebot
import json

with open('config.json') as f:
    config = json.load(f)

TOKEN = config["TELEGRAM_BOT_TOKEN"]
bot = telebot.TeleBot(TOKEN)


# Очікуємо email від користувачів
waiting_for_email = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    first_name = message.chat.first_name or "Користувач"

    bot.reply_to(message, f"Привіт, {first_name}! Введіть свій email:")
    
    waiting_for_email[chat_id] = True
    print(f"Очікуємо email від {first_name} (chat_id: {chat_id})")

@bot.message_handler(func=lambda message: message.chat.id in waiting_for_email)
def get_email(message):
    from app import db, User, app

    chat_id = message.chat.id
    email = message.text.strip()

    with app.app_context():

        user = User.query.filter_by(email=email).first()
        
        if user:
            user.telegram_id = str(chat_id)
            db.session.commit()
            bot.reply_to(message, f"Ваш Telegram успішно прив’язано до {email}!")
            print(f"✅ Прив’язано chat_id: {chat_id} до {email}")
            del waiting_for_email[chat_id]
        else:
            bot.reply_to(message, "Цей email не знайдено. Перевірте правильність введення.")

def send_telegram_message(user_email, text):
    from app import User, app
    
    with app.app_context():
        
        user = User.query.filter_by(email=user_email).first()
        if user and user.telegram_id:
            bot.send_message(user.telegram_id, text)


if __name__ == "__main__":
    print("Бот запущено...")
    bot.polling(none_stop=True)