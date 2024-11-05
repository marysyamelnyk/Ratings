from bs4 import BeautifulSoup
import requests
import schedule
import time
from typing import Dict, List

#url = 'https://ref-rating.com.ua/rating/studenthelp-com-ua'
#tags = 'a', 'span'
#adress = class:'review-count review-count_margin-left', itemprop: 'reviewCount'

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

            change_result = self.compare_reviews(reviews)

            if change_result == "Updating reviews.":
                print (f"Reviews number: {reviews}")
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
        

if __name__ == "__main__":

    platform = Platform(
        url='https://ref-rating.com.ua/rating/studenthelp-com-ua',
        tag='span',
        address='itemprop',
        review_attribute='reviewCount'
    )
    platform.pars_rating()


#schedule.every(10).seconds.do(lambda: pars_rating(url, tag, classes))

#while True:
    #schedule.run_pending()
    #time.sleep(1)