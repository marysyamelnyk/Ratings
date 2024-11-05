from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from .handlers import start, input_received, handle_confirmation, attribute_confirm, cancel
from .states import URL, URL_CONFIRM, TAG, TAG_CONFIRM, ADDRESS, ADDRESS_CONFIRM, ATTRIBUTE, ATTRIBUTE_CONFIRM
import settings

def main():
    application = ApplicationBuilder().token(settings.API_KEY).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: input_received(u, c, 'url', URL_CONFIRM))],
            URL_CONFIRM: [CallbackQueryHandler(lambda u, c: handle_confirmation(u, c, TAG, 'Great! Now, please send the HTML tag for the reviews:'), pattern='^(yes|no)$')],
            TAG: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: input_received(u, c, 'tag', TAG_CONFIRM))],
            TAG_CONFIRM: [CallbackQueryHandler(lambda u, c: handle_confirmation(u, c, ADDRESS, 'Please provide the attribute type (e.g., class, id):'), pattern='^(yes|no)$')],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: input_received(u, c, 'address', ADDRESS_CONFIRM))],
            ADDRESS_CONFIRM: [CallbackQueryHandler(lambda u, c: handle_confirmation(u, c, ATTRIBUTE, 'Finally, please provide the attribute value (e.g., reviewCount):'), pattern='^(yes|no)$')],
            ATTRIBUTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: input_received(u, c, 'review_attribute', ATTRIBUTE_CONFIRM))],
            ATTRIBUTE_CONFIRM: [CallbackQueryHandler(attribute_confirm, pattern='^(yes|no)$')]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()