import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import re

def generate_rss():
    # 나라일터 모집공고 URL
    url = "https://www.gojobs.go.kr/apmList.do?menuNo=401&mngrMenuYn=N&selMenuNo=400&upperMenuNo="
    
    # HTTP 요청 및 파싱
    response = requests.get(url, verify=False) # 공공기관 사이트 SSL 이슈 방지
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # RSS 피드 초기화
    fg = FeedGenerator()
    fg.title('나라일터 일반채용 모집공고')
    fg.link(href=url, rel='alternate')
    fg.description('인사혁신처 나라일터 시스템의 일반채용 모집공고 RSS 피드입니다.')
    fg.language('ko')
    
    # 게시판 목록 파싱 (테이블의 각 행 추출)
    rows = soup.select('table tbody tr')
    
    for row in rows:
        columns = row.find_all('td')
        # 정상적인 데이터 행인지 확인 (컬럼 개수가 부족하면 건너뜀)
        if len(columns) < 6:
            continue
            
        try:
            # 2번째 컬럼(인덱스 1)에 공고명과 링크가 존재함
            title_td = columns[1]
            title_tag = title_td.find('a')
            if not title_tag:
                continue
                
            title = title_tag.get_text(strip=True)
            href = title_tag.get('href', '')
            
            # 자바스크립트 함수(ex: javascript:fn_view('1234')) 형태인 경우 게시글 번호 추출
            link = url
            post_id_match = re.search(r"'(.*?)'", href)
            if post_id_match:
                # 상세 페이지 URL 조합 (사이트 구조에 맞게 변경 필요)
                post_id = post_id_match.group(1)
                link = f"https://www.gojobs.go.kr/apmView.do?dtyNo={post_id}&menuNo=401"
            elif href.startswith('http') or href.startswith('/'):
                link = "https://www.gojobs.go.kr" + href if href.startswith('/') else href

            # 기관명, 게시일, 마감일 파싱
            institution = columns[2].get_text(strip=True)
            post_date = columns[3].get_text(strip=True)
            deadline = columns[4].get_text(strip=True)
            
            # RSS 아이템(엔트리) 추가
            fe = fg.add_entry()
            fe.title(f"[{institution}] {title}")
            fe.link(href=link)
            fe.description(f"<b>기관명:</b> {institution}<br><b>공고게시일:</b> {post_date}<br><b>접수마감일:</b> {deadline}")
            fe.guid(link)
            
        except Exception as e:
            print(f"항목 파싱 에러: {e}")
            continue
            
    # 완성된 RSS를 xml 파일로 저장
    fg.rss_file('rss.xml')
    print("rss.xml 파일이 성공적으로 생성되었습니다.")

if __name__ == "__main__":
    generate_rss()
