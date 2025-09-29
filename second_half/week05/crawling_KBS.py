#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 로그인 크롤링 프로그램
셀레니움을 사용하여 네이버에 로그인하고 로그인 후 콘텐츠를 크롤링합니다.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


class NaverCrawler:
    """네이버 크롤링을 위한 클래스"""
    
    def __init__(self):
        """크롤러 초기화"""
        self.driver = None
        self.wait = None
        self.crawled_content = []
    
    def setup_driver(self):
        """셀레니움 드라이버 설정"""
        chrome_options = Options()
        
        # 기본 옵션
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-images')
        
        # User-Agent 설정 (일반 브라우저로 위장)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # ChromeDriver 자동 관리 (webdriver-manager 사용)
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except ImportError:
            # webdriver-manager가 없는 경우 시스템 PATH의 chromedriver 사용
            self.driver = webdriver.Chrome(options=chrome_options)
        
        # 자동화 감지 우회를 위한 스크립트 실행
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, 10)
    
    def login_to_naver(self, username, password):
        """네이버에 로그인"""
        try:
            # 네이버 로그인 페이지로 이동
            self.driver.get('https://nid.naver.com/nidlogin.login')
            time.sleep(2)  # 페이지 로딩 대기
            
            # 인간적인 행동을 시뮬레이션하기 위한 랜덤 대기
            import random
            time.sleep(random.uniform(1, 3))
            
            # 아이디 입력
            id_input = self.wait.until(
                EC.presence_of_element_located((By.ID, 'id'))
            )
            id_input.clear()
            self._human_type(id_input, username)
            
            # 비밀번호 입력
            pw_input = self.driver.find_element(By.ID, 'pw')
            pw_input.clear()
            self._human_type(pw_input, password)
            
            # 로그인 버튼 클릭 전 잠시 대기
            time.sleep(random.uniform(1, 2))
            
            # 로그인 버튼 클릭
            login_button = self.driver.find_element(By.ID, 'log.login')
            login_button.click()
            
            # 캡챠 확인 및 처리
            if self._handle_captcha():
                # 로그인 완료 대기
                time.sleep(3)
                
                # 로그인 성공 확인
                if 'naver.com' in self.driver.current_url and 'nid.naver.com' not in self.driver.current_url:
                    print('로그인 성공')
                    return True
                else:
                    print('로그인 실패 - 캡챠 또는 인증 문제')
                    return False
            else:
                print('캡챠 처리 실패')
                return False
                
        except Exception as e:
            print(f'로그인 중 오류 발생: {e}')
            return False
    
    def _human_type(self, element, text):
        """인간적인 타이핑 시뮬레이션"""
        import random
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))  # 각 문자 입력 간 랜덤 대기
    
    def _handle_captcha(self):
        """캡챠 처리"""
        try:
            # 캡챠가 나타나는지 확인 (몇 초 대기)
            time.sleep(3)
            
            # 캡챠 관련 요소들 확인
            captcha_selectors = [
                'iframe[src*="captcha"]',
                '.captcha',
                '#captcha',
                '.g-recaptcha',
                'iframe[title*="captcha"]'
            ]
            
            for selector in captcha_selectors:
                try:
                    captcha_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if captcha_element.is_displayed():
                        print('캡챠가 감지되었습니다.')
                        return self._solve_captcha()
                except:
                    continue
            
            # 캡챠가 없는 경우
            return True
            
        except Exception as e:
            print(f'캡챠 처리 중 오류: {e}')
            return False
    
    def _solve_captcha(self):
        """캡챠 해결 시도"""
        print('캡챠 해결을 시도합니다...')
        
        # 방법 1: 사용자에게 수동 입력 요청
        try:
            # 캡챠 이미지가 있는지 확인
            captcha_image = self.driver.find_element(By.CSS_SELECTOR, 'img[src*="captcha"], .captcha img')
            if captcha_image.is_displayed():
                print('캡챠 이미지를 발견했습니다.')
                print('브라우저 창에서 캡챠를 수동으로 해결해주세요.')
                print('해결 후 Enter를 눌러주세요...')
                input()  # 사용자 입력 대기
                return True
        except:
            pass
        
        # 방법 2: 자동 새로고침으로 캡챠 우회 시도
        try:
            print('캡챠 우회를 위해 페이지를 새로고침합니다...')
            self.driver.refresh()
            time.sleep(3)
            return True
        except:
            pass
        
        # 방법 3: 다른 로그인 방법 시도 (QR코드 등)
        try:
            qr_button = self.driver.find_element(By.CSS_SELECTOR, '.qr_login, .qr-login')
            if qr_button.is_displayed():
                print('QR코드 로그인을 시도합니다.')
                qr_button.click()
                time.sleep(5)
                print('QR코드로 로그인을 완료한 후 Enter를 눌러주세요...')
                input()
                return True
        except:
            pass
        
        print('캡챠 해결에 실패했습니다.')
        return False
    
    def crawl_naver_content(self):
        """네이버 로그인 후 콘텐츠 크롤링"""
        try:
            # 네이버 메인 페이지로 이동
            self.driver.get('https://www.naver.com')
            time.sleep(2)
            
            # 로그인 후에만 보이는 콘텐츠들 크롤링
            crawled_items = []
            
            # 1. 사용자 정보 (프로필 영역)
            try:
                profile_element = self.driver.find_element(By.CLASS_NAME, 'MyView-module__link_login___HpHMW')
                profile_text = profile_element.text
                crawled_items.append(f'프로필: {profile_text}')
            except:
                pass
            
            # 2. 메일 알림 (새 메일 수)
            try:
                mail_elements = self.driver.find_elements(By.CSS_SELECTOR, '.mail_count')
                for mail in mail_elements:
                    if mail.text.strip():
                        crawled_items.append(f'메일 알림: {mail.text.strip()}')
            except:
                pass
            
            # 3. 네이버페이 포인트 정보
            try:
                naver_pay_elements = self.driver.find_elements(By.CSS_SELECTOR, '.naver_pay')
                for pay in naver_pay_elements:
                    if pay.text.strip():
                        crawled_items.append(f'네이버페이: {pay.text.strip()}')
            except:
                pass
            
            # 4. 쇼핑 관련 개인화 콘텐츠
            try:
                shopping_elements = self.driver.find_elements(By.CSS_SELECTOR, '.shopping_my')
                for shop in shopping_elements:
                    if shop.text.strip():
                        crawled_items.append(f'쇼핑: {shop.text.strip()}')
            except:
                pass
            
            # 5. 개인화된 뉴스 추천
            try:
                news_elements = self.driver.find_elements(By.CSS_SELECTOR, '.news_area')
                for news in news_elements[:3]:  # 상위 3개만
                    if news.text.strip():
                        crawled_items.append(f'뉴스: {news.text.strip()[:50]}...')
            except:
                pass
            
            self.crawled_content = crawled_items
            return crawled_items
            
        except Exception as e:
            print(f'크롤링 중 오류 발생: {e}')
            return []
    
    def crawl_naver_mail_titles(self):
        """네이버 메일 제목 크롤링 (보너스 과제)"""
        try:
            # 네이버 메일 페이지로 이동
            self.driver.get('https://mail.naver.com')
            time.sleep(3)
            
            mail_titles = []
            
            # 메일 제목들 찾기
            try:
                title_elements = self.driver.find_elements(By.CSS_SELECTOR, '.mail_title, .subject')
                for title in title_elements[:10]:  # 최근 10개 메일
                    if title.text.strip():
                        mail_titles.append(title.text.strip())
            except:
                pass
            
            return mail_titles
            
        except Exception as e:
            print(f'메일 크롤링 중 오류 발생: {e}')
            return []
    
    def display_results(self):
        """크롤링 결과 출력"""
        print('\n=== 네이버 로그인 후 크롤링 결과 ===')
        for i, content in enumerate(self.crawled_content, 1):
            print(f'{i}. {content}')
    
    def close_driver(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()


def main():
    """메인 함수"""
    # 사용자 정보 입력
    username = input('네이버 아이디를 입력하세요: ')
    password = input('네이버 비밀번호를 입력하세요: ')
    
    crawler = NaverCrawler()
    
    try:
        # 드라이버 설정
        print('셀레니움 드라이버를 설정합니다...')
        crawler.setup_driver()
        
        # 네이버 로그인
        print('네이버에 로그인합니다...')
        if crawler.login_to_naver(username, password):
            # 로그인 후 콘텐츠 크롤링
            print('로그인 후 콘텐츠를 크롤링합니다...')
            crawler.crawl_naver_content()
            
            # 결과 출력
            crawler.display_results()
            
            # 보너스: 메일 제목 크롤링
            print('\n=== 네이버 메일 제목 (보너스 과제) ===')
            mail_titles = crawler.crawl_naver_mail_titles()
            for i, title in enumerate(mail_titles, 1):
                print(f'{i}. {title}')
        else:
            print('로그인에 실패했습니다.')
    
    except Exception as e:
        print(f'프로그램 실행 중 오류 발생: {e}')
    
    finally:
        # 드라이버 종료
        crawler.close_driver()


if __name__ == '__main__':
    main()
