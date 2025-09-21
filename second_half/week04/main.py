import re
import sys
import requests
from bs4 import BeautifulSoup


def fetch_kbs_news():
    """
    KBS 뉴스 사이트에서 헤드라인 뉴스를 가져옵니다.
    """
    url = 'http://news.kbs.co.kr/news/pc/main/main.html'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 링크가 있는 모든 텍스트 중에서 뉴스 제목 추출
        links = soup.find_all('a')
        news_headlines = []
        
        for link in links:
            text = link.get_text().strip()
            
            # 시간 형식으로 시작하는 항목 필터링 (예: "06:00", "07:00" 등)
            time_pattern = r'^\d{1,2}:\d{2}'
            
            # 뉴스 제목으로 보이는 조건들
            if (text and len(text) > 10 and len(text) < 100 and 
                not text.startswith('http') and 
                not re.match(time_pattern, text) and  # 시간 형식 필터링 추가
                not text in ['더보기', 'ON AIR', 'English', '재난포털', '제보'] and
                any(keyword in text for keyword in ['…', '·', ':', '(', ')', '경제', '사회', '정치', '국제'])):
                news_headlines.append(text)
        
        # 중복 제거 (순서 유지)
        unique_headlines = list(dict.fromkeys(news_headlines))
        
        return unique_headlines
        
    except requests.RequestException as e:
        print(f'뉴스 데이터를 가져오는 중 오류가 발생했습니다: {e}')
        print('프로그램을 종료합니다.')
        sys.exit(1)
    except Exception as e:
        print(f'예상치 못한 오류가 발생했습니다: {e}')
        print('프로그램을 종료합니다.')
        sys.exit(1)


def display_headlines(headlines):
    """
    헤드라인 리스트를 화면에 출력합니다.
    """
    if not headlines:
        print('헤드라인을 찾을 수 없습니다.')
        return
    
    print('=== KBS 뉴스 헤드라인 ===')
    for i, headline in enumerate(headlines, 1):
        print(f'{i}. {headline}')


if __name__ == '__main__':
    """
    메인 함수: KBS 뉴스 헤드라인을 가져와서 출력합니다.
    """
    print('KBS 뉴스 헤드라인을 가져오는 중...')
    headlines = fetch_kbs_news()
    display_headlines(headlines)
