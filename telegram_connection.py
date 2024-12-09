from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, BotCommand
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes
)
import settings
from ratings import Platform

# Стани для ConversationHandler
URL, URL_CONFIRM, TAG, TAG_CONFIRM, ADDRESS, ADDRESS_CONFIRM, ATTRIBUTE, ATTRIBUTE_CONFIRM = range(8)

platform = Platform(
    url='https://example.com',  # Тимчасова URL
    tag='span',
    address='class',
    review_attribute='reviewCount'
)

# Команда старту
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [['/check', '/clear', '/reset'], ['/cancel']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        'Welcome! Please use the commands below or follow the instructions.',
        reply_markup=reply_markup
    )
    return URL

# Команда для перевірки рейтингу
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = platform.pars_rating()
    await update.message.reply_text(response)

# Команда для очищення списку відгуків
async def clear_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = platform.clear_file()
    await update.message.reply_text(response)

# Команда для збросу даних
async def reset_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = platform.reset_data()
    await update.message.reply_text(response)


# Обробка введеної URL
async def url_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['url'] = update.message.text
    return await confirm_input(update, context, context.user_data['url'], URL_CONFIRM)

async def url_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_confirmation(update, context, TAG, 'Great! Now, please send the HTML tag for the reviews:')

# Обробка введеного тегу
async def tag_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['tag'] = update.message.text
    return await confirm_input(update, context, context.user_data['tag'], TAG_CONFIRM)

async def tag_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_confirmation(update, context, ADDRESS, 'Please provide the attribute type (e.g., class, id):')

# Обробка введеної адреси
async def address_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['address'] = update.message.text
    return await confirm_input(update, context, context.user_data['address'], ADDRESS_CONFIRM)

# Обробка введеного атрибуту
async def address_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_confirmation(update, context, ATTRIBUTE, 'Finally, please provide the attribute value (e.g., reviewCount):')

async def attribute_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['review_attribute'] = update.message.text
    return await confirm_input(update, context, context.user_data['review_attribute'], ATTRIBUTE_CONFIRM)


# Підтвердження атрибуту та перевірка
async def attribute_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    platform = Platform(
        url=context.user_data['url'],
        tag=context.user_data['tag'],
        address=context.user_data['address'],
        review_attribute=context.user_data['review_attribute']
    )
    result = platform.pars_rating()
    await update.message.reply_text(result, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

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
        await update.message.reply_text(prompt_text, reply_markup=ReplyKeyboardRemove())
        return next_state
    else:
        await update.message.reply_text('Let\'s start over.', reply_markup=ReplyKeyboardRemove())
        return await start(update, context)

# Команда для скасування
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Process cancelled.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Основна функція для запуску бота
def main():
    application = ApplicationBuilder().token(settings.API_KEY).build()

# Обробник розмовного процесу
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, url_received)],
            URL_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, url_confirm)],
            TAG: [MessageHandler(filters.TEXT & ~filters.COMMAND, tag_received)],
            TAG_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, tag_confirm)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address_received)],
            ADDRESS_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, address_confirm)],
            ATTRIBUTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, attribute_received)],
            ATTRIBUTE_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, attribute_confirm)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

# Обробники для команд
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('check', check))
    application.add_handler(CommandHandler('clear', clear_data))
    application.add_handler(CommandHandler('reset', reset_data))
   
# Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()  