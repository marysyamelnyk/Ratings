from lxml import html
import requests


class Platform:

    def __init__(self, url: str, xpath: str) -> None:
        self.url = url
        self.xpath = xpath

    def parser(self):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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
            
            return f"Reviews: {reviews}"
        except Exception as e:
            return f"Error parsing page: {e}"

    
