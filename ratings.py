from bs4 import BeautifulSoup
import requests
import os
from typing import Dict, List


class Platform:
    def __init__(self, url: str, tag: str, address: str, review_attribute: str) -> None:
        self.url = url
        self.tag = tag
        self.address = address
        self.review_attribute = review_attribute

        self.reviews_rating: Dict[str, List[str]] = {}
        self._load_reviews()

    def _load_reviews(self) -> None:
      # Зчитуємо файл та заповнюємо словник наявними даними  
        file_path = 'reviews.txt'

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                lines = f.readlines()
            for line in lines:
                parts = line.strip().split(" Reviews number: ")
                if len(parts) == 2:
                    self.reviews_rating[parts[0]] = parts[1]

    def pars_rating(self) -> str:
        try: 
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
            }
            response = requests.get(self.url, headers=headers, allow_redirects=False)
            response.raise_for_status()
    
            soup = BeautifulSoup(response.text, "html.parser")
        # Витягуємо потрібну інфу з сайту    
            reviews_element = soup.find(self.tag, {self.address: self.review_attribute})
            print("Found reviews_element:", reviews_element)
        # Робимо її гарною (витягуємо тільки кі-сть відгуків)    
            reviews = reviews_element.text.strip() if reviews_element else "No matches found."
            print(reviews)
        # Виклик функціїї яка дає нам зрозуміти зміни в кі-стях
            change_result = self.compare_reviews(reviews)
            return change_result

        except requests.exceptions.TooManyRedirects:
            return "Too many redirects occurred. Please check the URL."
        except requests.exceptions.RequestException as e:
            return f"An error occurred while fetching the reviews: {e}"

    def compare_reviews(self, reviews: str) -> str:
        
       # Перевіряємо наявність такого url в існуючих
        if self.url in self.reviews_rating:
            existing_reviews = self.reviews_rating[self.url]
            if existing_reviews == reviews:
                print("No changes have been detected.")
                return "No changes have been detected."
            else:
            # Оновлюємо значення в словнику    
                self.reviews_rating[self.url] = reviews
        else:
          # Додаємо значення якщо такого не було  
            self.reviews_rating[self.url] = reviews

      # Перезаписуємо файл з оновленими даними        
        self._save_reviews()
        print("Review has been updated.")    
        return "Review has been updated."
    
    def _save_reviews(self) -> None:
        with open('reviews.txt', 'w') as f:
            for url, review_count in self.reviews_rating.items():
                f.write(f"{url} Reviews number: {review_count}\n")




        

if __name__ == "__main__":

    platform = Platform(
        url='https://ref-rating.com.ua/rating/studenthelp-com-ua',
        tag='span',
        address='itemprop',
        review_attribute='reviewCount'
    )
    print(platform.pars_rating())

    platform2 = Platform(
        url='https://www.otzyvua.net/uk/hotlaynhotline.html',
        tag='span',
        address='class',
        review_attribute='count'
    )
    print(platform2.pars_rating())