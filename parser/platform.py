from bs4 import BeautifulSoup
import requests
from typing import Dict, Optional

class Platform:
    def __init__(self, url: str, tag: str, address: str, review_attribute: str) -> None:
        self.url = url
        self.tag = tag
        self.address = address
        self.review_attribute = review_attribute
        self.reviews_rating: Dict[str, str] = {}

    def parse_rating(self) -> str:
        page_content = self._fetch_content_with_redirect_limit()
        if page_content is None:
            return "Couldn't get the page content."
        elif "Too many redirects" in page_content:
            return page_content

        reviews = self._extract_reviews_count(page_content)
        return self._compare_reviews(reviews)

    def _fetch_content_with_redirect_limit(self, max_redirects: int = 5) -> Optional[str]:
        session = requests.Session()
        try:
            response = session.get(self.url, allow_redirects=True)
            if len(response.history) > max_redirects:
                return "Too many redirects: over max limit."
            response.raise_for_status()
            return response.text
        except requests.exceptions.TooManyRedirects:
            return "Error: too many redirects. Check URL."
        except requests.exceptions.RequestException as e:
            return f"Error while loading reviews: {e}"

    def _extract_reviews_count(self, page_content: str) -> str:
        soup = BeautifulSoup(page_content, "html.parser")
        reviews_element = soup.find(self.tag, {self.address: self.review_attribute})
        return reviews_element.text.strip() if reviews_element else "Nothing found"

    def _compare_reviews(self, reviews: str) -> str:
        if not reviews or reviews == "Nothing found":
            return "Nothing found"