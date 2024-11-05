from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
from parser.platform import Platform
from bot.states import URL, URL_CONFIRM, TAG, TAG_CONFIRM, ADDRESS, ADDRESS_CONFIRM, ATTRIBUTE, ATTRIBUTE_CONFIRM

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await prompt_user(update, "Please send the URL of the website you want to reach:")

async def input_received(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str, next_state: int) -> int:
    context.user_data[key] = update.message.text
    return await confirm_input(update, context, context.user_data[key], next_state)

async def confirm_input(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str, next_state: int) -> int:
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data='yes')],
        [InlineKeyboardButton("No", callback_data='no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
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

async def attribute_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.callback_query:
        await update.message.reply_text("An unexpected error occurred. Please try again.")
        return ConversationHandler.END
    
    platform = Platform(
        url=context.user_data.get('url', ''),
        tag=context.user_data.get('tag', ''),
        address=context.user_data.get('address', ''),
        review_attribute=context.user_data.get('review_attribute', '')
    )
    try:
        result = platform.parse_rating() or "No data found or an error occurred during parsing."
    except Exception as e:
        result = f"An error occurred: {e}"

    await update.callback_query.edit_message_text(result)
    return ConversationHandler.END

async def prompt_user(update: Update, message: str) -> int:
    if update.message:
        await update.message.reply_text(message)
    return URL

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Process cancelled.')
    return ConversationHandler.END