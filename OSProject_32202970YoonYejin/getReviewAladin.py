import scrapy
import pandas as pd
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.ie.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



# 알라딘 사이트 유저의 리뷰를 크롤링 하는 scrapy spider
# 크롤링 모듈: scrapy, selenium
# 데이터 저장 모듈: pandas
class GetreviewaladinSpider(scrapy.Spider):
    name = "getReviewAladin"
    allowed_domains = ["www.aladin.co.kr"]
    start_urls = ["https://www.aladin.co.kr/home/welcome.aspx"]

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    
    # 크롤링 시작 함수
    def start_requests(self, title, author):
        # 도서 상세 페이지 url get
        urls = self.get_detailPage_url(title, author)
        
        if(urls == False):
            return False
        
        # 도서 상세 페이지에서 유저 리뷰와 도서 이미지 파일을 get
        reviews, img = self.get_reviews(urls)
        if(reviews is None):
            return False
        
        # csv 파일 저장
        self.save_as_csv(title, author, img, reviews)


    # 도서 상세 페이지에서 유저 리뷰와 도서 이미지 파일을 크롤링하는 함수
    def get_reviews(self, urls):
        driver = webdriver.Chrome('./chromedriver.exe', options=self.options)
        # 도서 상세 페이지 접속
        driver.get(urls)
        
        # 리뷰 창까지 스크롤
        try:
            action = ActionChains(driver)
            action.move_to_element(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="Ere_prod_allwrap"]/div[13]/div[1]')))).perform()
        except:
            return False
        
        # 리뷰 목록 더보기 클릭
        try:
            moreclick = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="divReviewPageMore"]')))
        except:
            return False
        
        # 10회 반복
        i = 0
        while(moreclick.get_attribute('style') != "display:none;"):
            try:
                driver.find_element(By.XPATH, '//*[@id="divReviewPageMore"]/div[1]/a').click()
                time.sleep(5)
                moreclick = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="divReviewPageMore"]')))
            except:
                break
            print('CLICK', i)
            i += 1
            if(i == 10): break
        
        # 리뷰 목록에서 유저 리뷰 텍스트만 추출
        # 유저 리뷰 텍스트를 포함하는 dom 요소들 추출
        reviews = list()
        try:
            reviewbox = driver.find_element(By.XPATH, '//*[@id="CommentReviewList"]')
            getReviews = reviewbox.find_elements(By.CLASS_NAME, 'hundred_list')
        except:
            return False
        
        print('Start REVIEWS', getReviews)
        # 유저 리뷰 텍스트 추출
        for r in getReviews:
            try:
                rtext = r.find_element(By.XPATH, './div[2]/div/ul/li[1]/div/div/a[1]').text
                reviews.append(rtext)
            except:
                return False
        # 도서 이미지 링크 추출 (알라딘 제공)
        img = driver.find_element(By.ID, 'CoverMainImage').get_attribute('src')    
        
        return reviews, img


    # 도서명으로 검색하여 찾는 도서의 상세 페이지 url를 얻는 함수
    def get_detailPage_url(self, title, author):
        # 검색창에 도서명 검색
        urls = "https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=All&KeyWord={title}".format(title=title)
        
        driver = webdriver.Chrome('./chromedriver', options=self.optㄱions)
        driver.get(urls)
        time.sleep(7)
        
        # 검색 결과의 도서 목록 추출
        try:
            booklist = driver.find_elements(By.XPATH, '//*[@id="Search3_Result"]/div[1]')
        except:
            return False
        
        # 도서 목록에서 찾는 저자와 일치하는 도서 탐색
        for book in booklist:
            book_author = book.find_element(By.XPATH, '//table/tbody/tr/td[3]/table/tbody/tr[1]/td[1]/div[1]/ul/li[3]/a[1]').text
            if (author in book_author):
                # 일치하는 도서의 itemid 추출
                itemId = book.get_attribute('itemid')
                # 상세 도서 페이지 url
                urls = "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId={itemId}".format(itemId=itemId)
                return urls

        return False
    
    
    # 크롤링 후 책제목, 글쓴이, 도서 이미지 링크, 유저 리뷰를 csv 파일에 저장하는 함수
    def save_as_csv(self, title, author, img, reviews):
        pwd = os.getcwd()
        trim_title = title.replace(" ", "_")
        trim_author = author.replace(" ", "_")
        fname = "db/"+trim_author+"_"+trim_title+".xlsx"
        filepath = os.path.join(pwd, fname)
        results = pd.DataFrame({
            'title':title,
            'author':author,
            'img':img,
            'comments':reviews})
        results.to_excel(excel_writer=filepath, index=False)

