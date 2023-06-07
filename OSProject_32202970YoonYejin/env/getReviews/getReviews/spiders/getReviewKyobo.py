import scrapy


class GetreviewkyoboSpider(scrapy.Spider):
    name = "getReviewKyobo"
    allowed_domains = ["www.kyobobook.co.kr"]
    start_urls = ["https://www.kyobobook.co.kr/"]

    def parse(self, response):
        pass
