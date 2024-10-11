from bs4 import BeautifulSoup
import requests
import schedule
import time
from typing import Dict, List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler, ContextTypes 

#url = 'https://ref-rating.com.ua/rating/studenthelp-com-ua'
#tags = 'a', 'span'
#adress = class:'review-count review-count_margin-left', itemprop: 'reviewCount'

URL, URL_CONFIRM, TAG, TAG_CONFIRM, ADDRESS, ADDRESS_CONFIRM, ATTRIBUTE, ATTRIBUTE_CONFIRM = range(8)

class Platform:
    def __init__(self, url: str, tag: str, address: str, review_attribute: str) -> None:
        self.url = url
        self.tag = tag
        self.address = address
        self.review_attribute = review_attribute

        self.reviews_rating: Dict[str, List[str]] = {}

    def pars_rating(self) -> str:
        try: 
            response = requests.get(self.url)
            response.raise_for_status()
    
            soup = BeautifulSoup(response.text, "html.parser")
            reviews_element = soup.find(self.tag, {self.address: self.review_attribute})
            reviews = reviews_element.text.strip() if reviews_element else "No matches found."

            # Перевірка та оновлення кількості відгуків
            change_result = self.compare_reviews(reviews)

            if change_result == "Updating reviews.":
                return f"Reviews number: {reviews}"
            else:
                return change_result

        except requests.exceptions.TooManyRedirects:
            return "Too many redirects occurred. Please check the URL."
        except requests.exceptions.RequestException as e:
            return f"An error occurred while fetching the reviews: {e}"

    def compare_reviews(self, reviews: str) -> str:
        if reviews is None:
            return "No matches found."
    
        if self.url not in self.reviews_rating:
            self.reviews_rating[self.url] = []

        last_review = self.reviews_rating[self.url][-1] if self.reviews_rating[self.url] else None

        if reviews != last_review:
            self.reviews_rating[self.url].append(reviews)
            return "Updating reviews."
        else:
            return "No changes detected in reviews."
        
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

    # Відправка повідомлення з варіантами вибору
    if isinstance(update, Update) and update.message:
        await update.message.reply_text(f"Are you sure about: {data}?", reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(f"Are you sure about: {data}?", reply_markup=reply_markup)
    
    return next_state

# Функція для обробки підтвердження
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
    application = ApplicationBuilder().token("7328718795:AAFNFD1rYF9O59Hm0lZoz7rRR2xEkYIzA_Y").build()

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



#if __name__ == "__main__":

    #platform = Platform(
        #url='https://ref-rating.com.ua/rating/studenthelp-com-ua',
        #tags='span',
        #adress='itemprop',
        #review_attribute='reviewCount'
    #)
    #platform.pars_rating()


#schedule.every(10).seconds.do(lambda: pars_rating(url, tags, classes))

#while True:
    #schedule.run_pending()
    #time.sleep(1)
