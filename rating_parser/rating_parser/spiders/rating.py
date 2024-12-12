import scrapy
from rating_parser import RatingParserItem
from platform_class import Platform

class RatingSpider(scrapy.Spider):
    name = "rating_spider"

    def __init__(self, url=None, xpath=None, *args, **kwargs):
        super(RatingSpider, self).__init__(*args, **kwargs)
        self.reviews_rating = {}
        self.url = url
        self.xpath = xpath

    def start_request(self):
        url = self.url 
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        try:
            ratings = response.xpath(self.xpath).getall()
            
            if not ratings:
                raise ValueError("No ratings found with the provided XPath.")
            
            # Створюємо об'єкт Platform для обробки відгуків
            platform = Platform(url = self.url, xpath = self.xpath)
            new_reviews = platform.compare_reviews(ratings)
            
            if new_reviews:
                platform._save_reviews(new_reviews)
                return {"new_reviews": new_reviews}
            else:
                return {"message": "No new reviews found."}
        
        except Exception as e:
            self.logger.error(f"Error processing XPath: {str(e)}")
            return {"error": str(e)}   

    