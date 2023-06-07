import scrapy


class Getreviewyes24Spider(scrapy.Spider):
    name = "getReviewYes24"
    allowed_domains = ["www.yes24.com"]
    start_urls = ["https://www.yes24.com/main/default.aspx"]

    def parse(self, response):
        pass
