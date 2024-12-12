import scrapy
from platform_class import Platform

class RatingSpider(scrapy.Spider):
    name = "rating_spider"

    def __init__(self, url=None, xpath=None, *args, **kwargs):
        super(RatingSpider, self).__init__(*args, **kwargs)
        self.url = url
        self.xpath = xpath

    def start_requests(self):
        if not self.url:
            self.logger.error("No URL provided.")
            return
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        try:
            ratings = response.xpath(self.xpath).getall()

            if not ratings:
                raise ValueError("No ratings found with the provided XPath.")

            # Формуємо текст відгуків як рядок для обробки у `Platform`
            ratings_text = "\n".join(ratings)

            # Обробляємо відгуки через `Platform`
            platform = Platform(url=self.url, xpath=self.xpath)
            result = platform.compare_reviews(ratings_text)

            # Лог результату
            self.logger.info(f"Result of parsing: {result}")
            return {"result": result}
        
        except Exception as e:
            self.logger.error(f"Error processing XPath: {str(e)}")
            return {"error": str(e)}
   

    