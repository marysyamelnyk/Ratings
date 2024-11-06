from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler, 
                          filters, ConversationHandler, CallbackQueryHandler, 
                          ContextTypes) 
import settings
from ratings import Platform

URL, URL_CONFIRM, TAG, TAG_CONFIRM, ADDRESS, ADDRESS_CONFIRM, ATTRIBUTE, ATTRIBUTE_CONFIRM = range(8)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Please send the URL of the website you want to reach:')
    return URL

async def receive_and_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE, state_key: str, next_state: int, prompt_text: str) -> int:
# Отримує дані від користувача та запитує підтвердження.
    context.user_data[state_key] = update.message.text
    return await confirm_input(update, context, context.user_data[state_key], next_state, prompt_text)

async def confirm_input(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str, next_state: int, prompt_text: str = '') -> int:
    """Функція для запиту підтвердження даних користувача."""
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data='yes')],
        [InlineKeyboardButton("No", callback_data='no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:  # Перевірка на наявність callback_query
        await update.callback_query.edit_message_text(f"Are you sure about: {data}?", reply_markup=reply_markup)
        if prompt_text:
            await update.callback_query.edit_message_text(prompt_text, reply_markup=reply_markup)
    elif update.message:  # Якщо це текстове повідомлення
        await update.message.reply_text(f"Are you sure about: {data}?", reply_markup=reply_markup)
        if prompt_text:
            await update.message.reply_text(prompt_text, reply_markup=reply_markup)

    return await handle_confirmation(update, context, next_state)



async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE, next_state: int) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == 'yes':
        return next_state
    else:
        return await start(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Process cancelled.')
    return ConversationHandler.END

async def attribute_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    platform = Platform(
        url=context.user_data['url'],
        tag=context.user_data['tag'],
        address=context.user_data['address'],
        review_attribute=context.user_data['review_attribute']
    )
    result = platform.pars_rating()
    await update.callback_query.edit_message_text(result)
    return ConversationHandler.END

# Спільна функція для обробки кожного етапу.
def create_step_handler(state_key, next_state, prompt_text):
    async def step_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        return await receive_and_confirm(update, context, state_key, next_state, prompt_text)
    return step_handler

def main():
    application = ApplicationBuilder().token(settings.API_KEY).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_step_handler('url', URL_CONFIRM, 'Great! Now, please send the HTML tag for the reviews:'))],
            URL_CONFIRM: [CallbackQueryHandler(handle_confirmation, pattern='^(yes|no)$')],
            TAG: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_step_handler('tag', TAG_CONFIRM, 'Please provide the attribute type (e.g., class, id):'))],
            TAG_CONFIRM: [CallbackQueryHandler(handle_confirmation, pattern='^(yes|no)$')],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_step_handler('address', ADDRESS_CONFIRM, 'Finally, please provide the attribute value (e.g., reviewCount):'))],
            ADDRESS_CONFIRM: [CallbackQueryHandler(handle_confirmation, pattern='^(yes|no)$')],
            ATTRIBUTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_step_handler('review_attribute', ATTRIBUTE_CONFIRM, 'Please confirm the attribute value you provided:'))],
            ATTRIBUTE_CONFIRM: [CallbackQueryHandler(attribute_confirm, pattern='^(yes|no)$')]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()

