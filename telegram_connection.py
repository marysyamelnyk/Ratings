from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes
)
import api_key
from platform_class import Platform

# Стани для ConversationHandler
URL, XPATH, CONFIRM, EDIT = range(4)


# Команда старту
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [['Check Rating', 'Clear File', 'Reset Data'], ['Cancel the proccess']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    context.user_data['url'] = None
    context.user_data['xpath'] = None

    await update.message.reply_text(
        'Welcome! Please use the commands below or follow the instructions.',
        reply_markup=reply_markup
    )
    return ConversationHandler.END

# Команда для перевірки рейтингу 
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Please send the URL of the website you want to check:',
        reply_markup=ReplyKeyboardRemove()
    )
    return URL

#Отримання url
async def url_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['url'] = update.message.text
    await update.message.reply_text('Great! Now send me an XPath.')
    return XPATH

#Отримання XPath     
async def xpath_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['xpath'] = update.message.text
    url = context.user_data.get('url', '')
    xpath = context.user_data.get('xpath', '')

    keyboard = [['Yes', 'No']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard = True, resize_keyboard = True)
    await update.message.reply_text(
        f"Here is the data you've provided:\n\n"
        f"URL: {url}\n"
        f"XPath: {xpath}\n\n"
        "Is this correct?",
        reply_markup=reply_markup
    )
    return CONFIRM


# Підтвердження даних та перевірка
async def info_confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text.strip().lower()
    if user_input == 'yes':
        return await process_platform(update, context)
    else:
        keyboard = [['Change url', 'Change XPath']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            'Which data would you like to change?',
            reply_markup=reply_markup
        )
        return EDIT


# Функція для зміни вхідних даних користувачем
async def edit_data(update: Update, context: ContextTypes.DEFAULT_TYPE)-> int:
    choice = update.message.text.lower()
    if choice == 'change url':
        await update.message.reply_text('Please, send the new url:')
        return URL
    else:
        await update.message.reply_text('Please, send the new XPath:')
        return XPATH


#Витягуємо потрібні дані з XPath та створюємо об'єкт класу Platform
async def process_platform(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = context.user_data.get('url')
    xpath = context.user_data.get('xpath')

    if not url or not xpath:
        await update.message.reply_text("URL or XPath is missing. Please provide valid inputs.")
        return ConversationHandler.END

    try:
        platform = Platform(url=url, xpath=xpath)
        
        # Перевірка, чи `parser` є асинхронним
        result = platform.parser()

        if not result:
            await update.message.reply_text("No result found or file is empty.")
        else:
            await update.message.reply_text(f"Parsing result:\n{result}")
    except Exception as e:
        await update.message.reply_text(f"An error {e} occurred while processing your request. Please try again later.")
    
    return ConversationHandler.END

# Команда для скасування
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Process cancelled.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Команда для скасування
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Process cancelled.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Команда для очищення списку відгуків
async def clear_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = context.user_data['url']
    xpath = context.user_data['xpath']

    platform = Platform(url = url, xpath = xpath)
    result = platform.clear_file()

    await update.message.reply_text(result)

# Команда для збросу даних
async def reset_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = context.user_data['url']
    xpath = context.user_data['xpath']

    platform = Platform(url = url, xpath = xpath)
    result = platform.reset_data()

    await update.message.reply_text(result)

# Основна функція для запуску бота
def main():
    application = ApplicationBuilder().token(api_key.API_KEY).build()

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
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, info_confirmed)],
            EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, info_confirmed)],
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