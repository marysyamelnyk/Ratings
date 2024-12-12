import re
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, BotCommand
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes
)
import settings
from ratings import Platform

# Стани для ConversationHandler
URL, XPATH, CONFIRM, EDIT = range(4)

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
    if update.message.text.lower() == 'yes':
        return await process_platform(update, context)
    else:
        keyboard = [['Change url', 'Change XPath']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            'Which data would you like to change?',
            reply_markup = reply_markup
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
    url = context.user_data['url']
    xpath = context.user_data['xpath']

    try:
        tag_match = re.search(r"//(\w+)\[\@(\w+)='([^']+)'\]", xpath)
        tag = tag_match.group(1) if tag_match else 'unknown'
        attribute = tag_match.group(2) if tag_match else ''
        attribute_value = tag_match.group(3) if tag_match else ''
        
        platform = Platform(
            url=url,
            tag=tag,
            address=attribute,
            review_attribute=attribute_value
        )
        result = platform.pars_rating()
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"Error processing XPath: {str(e)}")
    
    return ConversationHandler.END

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