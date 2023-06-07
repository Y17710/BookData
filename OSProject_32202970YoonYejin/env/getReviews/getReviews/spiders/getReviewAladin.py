import scrapy
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.ie.options import Options

"""
유저로부터 책 이름, 저자 받으면

검색
상세페이지 접속
크롤링
리턴

"""


class GetreviewaladinSpider(scrapy.Spider):
    name = "getReviewAladin"
    allowed_domains = ["www.aladin.co.kr"]
    start_urls = ["https://www.aladin.co.kr/home/welcome.aspx"]

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    
    def start_requests(self, title, author):
        urls = self.get_detailPage_url(title, author)
        
        if(urls == False):
            return False
        
        reviews = self.get_reviews(urls)
        if(len(reviews) == 0):
            return False
        
        # csv 파일 저장
        self.save_as_csv(title, author, reviews)


    def get_reviews(self, urls):
        driver = webdriver.Chrome('./chromedriver', options=self.options)
        driver.get(urls)
        moreclick = driver.find_element_by_xpath('//*[@id="divReviewPageMore"]')
        while(moreclick.get_attribute('style') != "display:none;"):
            moreclick.find_element_by_xpath('/div[1]/a').click()
            time.sleep(3)
        
        reviews = list(driver.find_elements_by_xpath('//*[@id="hundred_list"]/div[2]/div/ul/li[1]/div/div/a[1]/text()'))
        return reviews


    # https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=All&KeyWord={title}&page={num}
    def get_detailPage_url(self, title, author):
        urls = "https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=All&KeyWord={title}".format(title=title)
        
        driver = webdriver.Chrome('./chromedriver', options=self.options)
        driver.get(urls)
        
        if(driver.find_element_by_xpath('//*[@id="search_t_g"]/text()')
           == "에 대한  검색 결과가 없습니다."): return False
        
        # num = int(response.xpath('//*[@id="ss_f_g_l"]/text()').extract())
        for i in range(1, 26):
            getAuthor = driver.find_element_by_xpath('//*div[@id="ss_book_box"][{i}]//*[@id="Search3_Result"]/div[10]/table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/div[1]/ul/li[3]/a[1]'.format(i=i))
            
            if (getAuthor == author):
                itemId = driver.find_element_by_xpath('//*div[@id="ss_book_box"][0]').get_attribute('itemid')
                urls = "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId={itemId}".format(itemId=itemId)
                return urls

        return False
    
    
    def save_as_csv(self, title, author, reviews):
        results = pd.DataFrame({'title':title,
                                'author':author,
                                'comments':reviews})
        results.to_excel('{author}_{title}.xlsx'.format(author=author, title=title), index=False)

