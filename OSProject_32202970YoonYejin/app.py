# 오픈소스SW활용 1분반 32202970 윤예진
# 유저들의 도서 리뷰를 요약해서 보여주는 서비스

from flask import Flask, url_for, request, render_template
import scrapy
import getReviewAladin as sp
import RefineTextModule as rf
import pandas as pd

app = Flask(__name__)

# main page
@app.route('/', endpoint='main')
def index():
	return render_template('index.html')


# 책 DB 검색 서비스, 기존 csv 파일이 있다면 해당 파일으로 리뷰 요약을 한다.
@app.route('/search', methods=['GET'], endpoint='search')
def search():
    if request.method == "GET":
        title = request.args.get('title', '', str)
        author = request.args.get('author', '', str)
        
        # 공백 제거
        trim_author = author.replace(" ", "_")
        trim_title = title.replace(" ", "_")
        fname = ".\\db\\"+trim_author+"_"+trim_title+".xlsx"
        df = None
        
        # 기존 리뷰 저장 csv 파일 열기 시도
        try:
            df = pd.read_excel(fname)
        # 없다면 새로 리뷰 크롤링 시작
        except:
            # 크롤링 작업을 하는 scrap spider 객체
            spider = sp.GetreviewaladinSpider(scrapy.Spider)
            spider.start_requests(title, author)
            
            try:    # csv 열기 재시도
                df = pd.read_excel(fname)
            except:
                return False
            
        # csv에 저장된 리뷰를 RefineText 모듈로 요약
        re = rf.RefineText(trim_title, trim_author)
        re.refine(df)
        cmt = './static/img/wc/{author}_{title}.png'.format(author=trim_author, title=trim_title)
        img = df['img'][1]
    
    # 도서 이미지, 제목, 저자, 리뷰 요약을 포함하는 결과 화면 출력
    return result(author=author, title=title, fname=cmt, img=img)


# iframe(검색 창) 기본 화면
@app.route('/search/default', methods=['GET'], endpoint='search_default')
def search_default():
    return render_template('search_default.html')

# 검색 결과 출력
@app.route('/result', methods=['GET'], endpoint='result')
def result(author='', title='', fname='', img=''):
    return render_template('result.html', author=author, title=title, fname=fname, img=img)
    

    
if __name__ == '__main__':
	app.run(debug=True)