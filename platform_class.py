import os
from typing import Dict


class Platform:

    def __init__(self, url: str, xpath: str) -> None:
        self.url = url
        self.xpath = xpath

        self.reviews_rating: Dict[str, str] = {}
        self._load_reviews()

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