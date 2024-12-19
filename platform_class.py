import os
from typing import Dict
from lxml import html
import requests




class Platform:

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
            reviews = [element.text_content() for element in reviews_elements]

            result = self.compare_reviews(reviews)
            return f"{result}\n Reviews: {reviews}"
        
        except Exception as e:
            return f"Error parsing page: {e}"
    

# Завантажує наявні відгуки з файлу і заповнює словник. 
# Якщо файл не існує або порожній, словник залишиться порожнім.
    def _load_reviews(self) -> None:
      # Зчитуємо файл та заповнюємо словник наявними даними  
        file_path = 'reviews.txt'
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                lines = f.readlines()
            for line in lines:
                parts = line.strip().split("Reviews number: ")
                if len(parts) == 2:
                    self.reviews_rating[parts[0]] = parts[1]


# Порівнює нові відгуки з наявними в словнику і оновлює дані, якщо відгуки змінилися.
    def compare_reviews(self, reviews: str) -> str:
       # Перевіряємо наявність такого url в існуючих
        if self.url in self.reviews_rating:
            existing_reviews = self.reviews_rating[self.url]
            if existing_reviews == reviews:
                return "No changes have been detected."
            else:
            # Оновлюємо значення в словнику    
                self.reviews_rating[self.url] = reviews
        else:
          # Додаємо значення якщо такого не було  
            self.reviews_rating[self.url] = reviews

      # Перезаписуємо файл з оновленими даними        
        self._save_reviews()   
        return "Review has been updated."
        
# Перезаписує файл з оновленими відгуками.    
    def _save_reviews(self) -> None:
        try:
            with open('reviews.txt', 'w') as f:
                for url, review_count in self.reviews_rating.items():
                    f.write(f"{url} Reviews number: {review_count}\n")

        except Exception as e:
            raise Exception(f"Error saving reviews: {str(e)}")            

# Очищує файл і словник.
    def clear_file(self) -> None:
        try:
            file_path = 'reviews.txt'
            if os.path.exists(file_path):
                open("reviews.txt", 'w').close()
                self.reviews_rating.clear()
                return "File and data have been cleared."
            else:
                return "File is already empty."
            
        except Exception as e:
            return f"Error clearing file: {str(e)}"    

# Скидає дані, завантажуючи відгуки з файлу.        
    def reset_data(self) -> str:
        try:
            self._load_reviews()
            return "Data has been reset from the file."    

        except Exception as e:
            return f"Error resetting data: {str(e)}"