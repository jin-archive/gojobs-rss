import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import os

def generate_rss():
    url = "https://www.gojobs.go.kr/apmList.do?menuNo=401&mngrMenuYn=N&selMenuNo=400&upperMenuNo="
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    fg = FeedGenerator()
    fg.title('공공기관 채용정보 (GOJOBS)')
    fg.link(href=url, rel='alternate')
    fg.description('공공기관 채용정보 실시간 업데이트 피드입니다.')
    fg.language('ko')

    # 사이트 구조 분석에 기반한 목록 추출 (보통 tr 태그)
    rows = soup.select('table.board_list tbody tr')

    for row in rows:
        try:
            title_tag = row.select_one('td.subject a')
            if not title_tag: continue
            
            title = title_tag.get_text(strip=True)
            link = "https://www.gojobs.go.kr" + title_tag['href']
            date_str = row.select('td')[-2].get_text(strip=True) # 날짜 칸 추출

            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=link)
            fe.description(f"등록일: {date_str}")
            fe.pubDate(datetime.now().astimezone()) 
        except:
            continue

    fg.rss_file('gojobs_rss.xml')

if __name__ == "__main__":
    generate_rss()
