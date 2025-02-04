import os
from typing import Dict, List
from lxml import html
import requests
import threading

class Platform:
    _lock = threading.Lock()

    def __init__(self, url: str, xpath: str) -> None:
        self.url = url
        self.xpath = xpath
        self.reviews_rating: Dict[str, str] = {}
        self._load_reviews()

    def parser(self):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
            }
            page = requests.get(self.url, headers=headers, allow_redirects=False)
            page.raise_for_status()
        except requests.RequestException as e:
            return f"Error fetching page: {e}"

        try:
            tree = html.fromstring(page.content)
            reviews_elements = tree.xpath(self.xpath)

            if reviews_elements and isinstance(reviews_elements[0], html.HtmlElement):
                reviews = [element.text.strip() for element in reviews_elements if element.text and element.text.strip()]
            elif reviews_elements:
                reviews = [text.strip() for text in reviews_elements if text.strip()]
            else:
                reviews = []    
            

            result = self.compare_reviews(reviews)
            return f"{result}\n Reviews: {reviews}"
        except Exception as e:
            return f"Error parsing page: {e}"

    def _load_reviews(self) -> None:
        file_path = 'reviews.txt'
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                lines = f.readlines()
            for line in lines:
                parts = line.strip().split(" Reviews number: ")
                if len(parts) == 2:
                    url, reviews = parts
                    self.reviews_rating[url] = reviews.strip()

    def compare_reviews(self, reviews: List[str]) -> str:
        reviews_str = ", ".join(reviews)

        if self.url in self.reviews_rating:
            existing_reviews = self.reviews_rating[self.url]
            if existing_reviews == reviews_str:
                return "No changes have been detected."
            else:
                self.reviews_rating[self.url] = reviews_str
        else:
            self.reviews_rating[self.url] = reviews_str

        self._save_reviews()
        return "Review has been updated."

    def _save_reviews(self) -> None:
        file_path = 'reviews.txt'
        try:
            with self._lock:
                with open(file_path, 'w') as f:
                    for url, reviews in self.reviews_rating.items():
                        f.write(f"{url} Reviews number: {reviews}\n")
            print(f"Reviews saved successfully to {file_path}.")  # Логування
        except Exception as e:
            print(f"Error saving reviews: {e}")


    # Очищує файл і словник.
    def clear_file(self) -> None:
        file_path = 'reviews.txt'
        if os.path.exists(file_path):
            open("reviews.txt", 'w').close()
            self.reviews_rating.clear()
            return "File and data have been cleared."
        else:
            return "File is already empty."

# Скидає дані, завантажуючи відгуки з файлу.        
    def reset_data(self) -> str:
        self._load_reviews()
        return "Data has been reset from the file."

