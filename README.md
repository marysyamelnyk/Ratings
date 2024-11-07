Review Tracker

This project is a web scraping and Telegram bot system that retrieves and tracks review counts from specified websites, allowing users to monitor review changes for different platforms directly through a Telegram bot.

Features

Web Scraping: Fetches review counts from specified URLs using HTML tags and attributes.
Review Management: Tracks changes in review counts. Saves reviews in a text file (reviews.txt) for persistent tracking. Includes options to clear and reset the review data.
Telegram Bot Integration: Interactive bot for review monitoring. Commands to start review tracking, clear saved reviews, and reset data. Supports URL, tag, and attribute inputs to dynamically define what information to scrape.

Installation

Prerequisites
- Python 3.x
- Telegram Bot API Key (set in settings.py)

Dependencies

Install required packages using:
pip install -r requirements.txt

Usage

Run the Bot: Start the bot by running the telegram_connection.py file:
python telegram_connection.py

Commands:

/start: Begin the process to track a new URL for review monitoring.
/check: Check and display the current review count from the predefined URLs.
/clear: Clear all saved review data.
/reset: Reload review data from reviews.txt.

Review Tracking:

Users can specify the URL, HTML tag, attribute type, and value for reviews. The bot fetches the review count and saves it to reviews.txt.

File Overview

ratings.py: Handles scraping and review management.
reviews.txt: Stores review data for tracking purposes.
telegram_connection.py: Manages the Telegram bot and connects it with the scraping functionality.

License

This project is licensed under the MIT License.
