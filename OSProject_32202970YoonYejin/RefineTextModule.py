import re
import pandas as pd
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from konlpy.tag import Kkma
from wordcloud import WordCloud
from collections import Counter


# 크롤링한 리뷰 텍스트에서 의미 있는 단어만 추출하여 wordcloud 이미지로 반환하는 모듈
class RefineText():
    def __init__(self, title, author):
          self.title = title
          self.author = author
    
    # 리뷰 텍스트 정제 작업 시작
    def refine(self, df):
        # 리뷰 목록
        comments = df['comments'].to_list()

        tokenCMT = list()
        kkma = Kkma()
        # 품사가 명사인 것만 추출
        for c in comments:
            tokenCMT += kkma.nouns(c)
        
        # 추출 결과 cmd 창에 출력
        print('----- REFINE COMMENTS -----')
        print(tokenCMT)
        
        # 출력한 토큰(명사)에 대해 빈도 수 체크
        tokenCMT = Counter(tokenCMT)
        tags = tokenCMT.most_common(40)
        
        # 상위 40개 명사에 대해서 단어 시각화(WordCloud) 작업
        wc = WordCloud(font_path='./static/font/NanumGothicExtraBold.ttf',
                       background_color="white", colormap="Pastel1",
                       max_font_size=50)
        cloud = wc.generate_from_frequencies(dict(tags))
        # WordCloud 이미지 파일 저장
        cloud.to_file('./static/img/wc/{author}_{title}.png'.format(author=self.author, title=self.title))
        
    
    # 정규식을 히용하여 불필요한 문자(특수문자, 오타 등) 제거
    def text_clearing(self, text):
        hangul = re.compile('[^ ㄱ-ㅣ가-힣]+')
        result = hangul.sub('', text)
        return result