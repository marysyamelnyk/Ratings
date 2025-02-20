import telebot
import json

with open("config.json") as f:
    config = json.load(f)

TOKEN = config["TELEGRAM_BOT_TOKEN"]
bot = telebot.TeleBot(TOKEN)
