from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, BotCommand
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes
)
import settings
from ratings import Platform

# Стани для ConversationHandler
URL, XPATH, URL_CONFIRMED, XPATH_CONFIRMED, INFO_CONFIRMED = range(5)

# Команда старту
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [['Check Rating', 'Clear File', 'Reset Data'], ['Cancel the proccess']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        'Welcome! Please use the commands below or follow the instructions.',
        reply_markup=reply_markup
    )
    return ConversationHandler.END

# Команда для перевірки рейтингу 
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Please send the URL of the website you want to reach:',
        reply_markup=ReplyKeyboardRemove()
    )
    return URL


async def url_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['url'] = update.message.text
    return await handle_confirmation(update, context, URL_CONFIRMED, 'Great! Now send me an XPath.')
    
async def xpath_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['xpath'] = update.message.text
    return await handle_confirmation(update, context, XPATH_CONFIRMED, 'Please confirm your XPath.')


# Підтвердження даних та перевірка
async def info_confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    url = context.user_data.get('url')
    xpath = context.user_data.get('xpath')

    confirmation_message = f"Please confirm your data:\nURL: {url}\nXPath: {xpath}"
    # Викликаємо функцію підтвердження
    return await confirm_input(update, context, confirmation_message, 'confirmed')

# Функція для підтвердження вводу
async def confirm_input(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str, next_state: int) -> int:
    keyboard = [['Yes', 'No']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(f"Are you sure about: {data}?", reply_markup=reply_markup)
    return next_state

# Функція для обробки підтвердження
async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE, next_state: int, prompt_text: str) -> int:
    user_response = update.message.text

    if user_response.lower() == 'yes':
        # Перевірка наявності даних
        if 'url' not in context.user_data or 'xpath' not in context.user_data:
            await update.message.reply_text("Please provide both URL and XPath.")
            return ConversationHandler.END

        # Створення об'єкта Platform після підтвердження
        url = context.user_data['url']
        xpath = context.user_data['xpath']
        platform = Platform(url=url, xpath=xpath)

        result = platform.pars_rating()
        await update.message.reply_text(result, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
    elif user_response.lower() == 'no':
        # Скидання процесу
        await update.message.reply_text('Let\'s start over.', reply_markup=ReplyKeyboardRemove())
        return await start(update, context)
    
    else:
        await update.message.reply_text("Please respond with 'Yes' or 'No'.")
        return next_state

# Команда для скасування
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Process cancelled.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Команда для очищення списку відгуків
async def clear_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = Platform.clear_file()
    await update.message.reply_text(response)

# Команда для збросу даних
async def reset_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = Platform.reset_data()
    await update.message.reply_text(response)

# Основна функція для запуску бота
def main():
    application = ApplicationBuilder().token(settings.API_KEY).build()

# Обробник розмовного процесу
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.TEXT & filters.Regex('^Check Rating$'), check),
            MessageHandler(filters.TEXT & filters.Regex('^Clear File$'), clear_data),
            MessageHandler(filters.TEXT & filters.Regex('^Reset Data$'), reset_data),
            MessageHandler(filters.TEXT & filters.Regex('^Cancel the proccess$'), cancel),
        ],
        states={
            URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, url_received)],
            XPATH: [MessageHandler(filters.TEXT & ~filters.COMMAND, xpath_received)],
            URL_CONFIRMED: [MessageHandler(filters.TEXT & ~filters.COMMAND, info_confirmed)],
            XPATH_CONFIRMED: [MessageHandler(filters.TEXT & ~filters.COMMAND, info_confirmed)],
            INFO_CONFIRMED: [MessageHandler(filters.TEXT & ~filters.COMMAND, info_confirmed)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Обробники для команд
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('start', start))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()  