from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler, ContextTypes 
import settings
from ratings import Platform

URL, URL_CONFIRM, TAG, TAG_CONFIRM, ADDRESS, ADDRESS_CONFIRM, ATTRIBUTE, ATTRIBUTE_CONFIRM = range(8)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Please send the URL of the website you want to reach:')
    return URL

async def url_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['url'] = update.message.text
    return await confirm_input(update, context, context.user_data['url'], URL_CONFIRM)

async def url_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_confirmation(update, context, TAG, 'Great! Now, please send the HTML tag for the reviews:')

async def tag_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['tag'] = update.message.text
    return await confirm_input(update, context, context.user_data['tag'], TAG_CONFIRM)

async def tag_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_confirmation(update, context, ADDRESS, 'Please provide the attribute type (e.g., class, id):')

async def address_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['address'] = update.message.text
    return await confirm_input(update, context, context.user_data['address'], ADDRESS_CONFIRM)

async def address_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_confirmation(update, context, ATTRIBUTE, 'Finally, please provide the attribute value (e.g., reviewCount):')

async def attribute_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['review_attribute'] = update.message.text
    return await confirm_input(update, context, context.user_data['review_attribute'], ATTRIBUTE_CONFIRM)

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

async def confirm_input(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str, next_state: int) -> int:
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data='yes')],
        [InlineKeyboardButton("No", callback_data='no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if isinstance(update, Update) and update.message:
        await update.message.reply_text(f"Are you sure about: {data}?", reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(f"Are you sure about: {data}?", reply_markup=reply_markup)
    
    return next_state

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE, next_state: int, prompt_text: str) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == 'yes':
        await query.edit_message_text(prompt_text)
        return next_state
    else:
        return await start(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Process cancelled.')
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token(settings.API_KEY).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, url_received)],
            URL_CONFIRM: [CallbackQueryHandler(url_confirm, pattern='^(yes|no)$')],
            TAG: [MessageHandler(filters.TEXT & ~filters.COMMAND, tag_received)],
            TAG_CONFIRM: [CallbackQueryHandler(tag_confirm, pattern='^(yes|no)$')],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address_received)],
            ADDRESS_CONFIRM: [CallbackQueryHandler(address_confirm, pattern='^(yes|no)$')],
            ATTRIBUTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, attribute_received)],
            ATTRIBUTE_CONFIRM: [CallbackQueryHandler(attribute_confirm, pattern='^(yes|no)$')]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()