from bot_config import bot
import logging

logging.basicConfig(filename='bot.log', level=logging.INFO)

@bot.message_handler(commands=['start'])
def start(message):
    logging.info("Received /start command")
    chat_id = message.chat.id
    first_name = message.chat.first_name or "User"
    
    text = message.text.strip()
    logging.info(f"Message text: {text}")

    if message.text.startswith('/start '):
        received_hash = text.split(" ", 1)[1].strip()
        logging.info(f"Received hash: {received_hash}")
        logging.info(f"Message email: {received_hash}")

        from app import User, app, db
        logging.info("1 Start checking email...")

        with app.app_context():
            logging.info("2 Start checking email...")

            try:
                user = User.query.filter_by(email_sha256=received_hash).first()
                logging.info("User query executed.")
            except Exception as e:
                logging.error(f"Error executing query: {e}")
                bot.reply_to(message, "❌ Database error. Please try again later.")
                return

            logging.info("Before checking if user exists")

            if user is None:
                logging.warning(f"User with email_sha256 {received_hash} not found.")
                print(f"User {first_name} has not provided the correct data.")
                bot.reply_to(message, "❌ This email was not found. Please check your data.")
                return

            logging.info(f"Found user: {user.email}, Telegram ID: {user.telegram_id}")

            # Перевіряємо, чи цей chat_id вже прив’язаний до іншого юзера
            existing_user = User.query.filter_by(telegram_id=str(chat_id)).first()
            if existing_user and existing_user.email_sha256 != user.email_sha256:
                logging.warning(f"Telegram ID {chat_id} is already connected to {existing_user.email}")
                bot.reply_to(message, "❌ This Telegram account is already connected to another user.")
                return

            # Перевіряємо, чи сам користувач вже має telegram_id
            if user.telegram_id not in [None, '']:
                logging.info(f"User {user.email} is already connected with Telegram ID: {user.telegram_id}")
                bot.reply_to(message, f"❌ Your Telegram is already connected with {user.email}.")
                return

            # Підключаємо Telegram
            try:
                user.telegram_id = str(chat_id)
                db.session.commit()
                logging.info(f"✅ Connected chat_id: {chat_id} with {user.email}")
                bot.reply_to(message, f"✅ Your Telegram successfully connected with {user.email}!")
            except Exception as e:
                logging.error(f"Error committing to database: {e}")
                bot.reply_to(message, "❌ Error while saving to database. Please try again later.")
                return
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