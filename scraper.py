import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import os

def generate_rss():
    # 1. 대상 URL 및 헤더 설정 (브라우저인 척 하기)
    url = "https://www.gojobs.go.kr/apmList.do?menuNo=401&mngrMenuYn=N&selMenuNo=400&upperMenuNo="
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.gojobs.go.kr/'
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        fg = FeedGenerator()
        fg.title('공공기관 채용정보 (GOJOBS)')
        fg.link(href=url, rel='alternate')
        fg.description('공공기관 채용정보 실시간 업데이트 피드입니다.')
        fg.language('ko')

        # 2. 사이트의 실제 구조: 보통 클래스명이 없거나 다를 수 있으므로 table 태그를 직접 찾습니다.
        # 공고가 들어있는 테이블을 찾고 그 안의 tr 행들을 가져옵니다.
        table = soup.find('table') 
        if not table:
            print("테이블을 찾을 수 없습니다.")
            return
            
        rows = table.select('tbody tr')

        for row in rows:
            cols = row.find_all('td')
            # 게시판에 데이터가 없는 경우(예: "등록된 게시물이 없습니다") 건너뜁니다.
            if len(cols) < 3:
                continue

            try:
                # 제목과 링크가 있는 <a> 태그 찾기
                title_tag = row.find('a')
                if not title_tag:
                    continue

                title = title_tag.get_text(strip=True)
                
                # 링크 정제 (onclick 이벤트 등에서 주소를 추출하거나 기본 경로 결합)
                link_raw = title_tag.get('href', '')
                if 'javascript:fn_view' in link_raw:
                    # 자바스크립트 함수 호출 형태일 경우, 패턴을 분석해 URL로 변환 (예시 처리)
                    # 실제 상세 페이지 구조에 따라 수정이 필요할 수 있습니다.
                    link = url 
                else:
                    link = "https://www.gojobs.go.kr" + link_raw if link_raw.startswith('/') else link_raw

                # 날짜 추출 (보통 마지막 혹은 뒤에서 두번째 열)
                date_str = cols[-2].get_text(strip=True)

                fe = fg.add_entry()
                fe.title(title)
                fe.link(href=link)
                fe.description(f"기관명: {cols[1].get_text(strip=True)} | 등록일: {date_str}")
                fe.pubDate(datetime.now().astimezone())
            except Exception as e:
                print(f"행 처리 중 오류: {e}")
                continue

        # 3. 파일 저장
        fg.rss_file('gojobs_rss.xml')
        print(f"성공: {len(fg.entry())}개의 공고를 찾았습니다.")

    except Exception as e:
        print(f"전체 프로세스 오류: {e}")

if __name__ == "__main__":
    generate_rss()
