import http.server
import socketserver
import datetime
import os
import sys


class SpacePirateHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """GET 요청 처리"""
        # 접속 정보 로깅
        self.log_access()
        
        # index.html 파일이 요청된 경우
        if self.path == '/' or self.path == '/index.html':
            self.serve_index_html()
        else:
            # 다른 파일 요청 시 기본 처리
            super().do_GET()
    
    def serve_index_html(self):
        """index.html 파일을 제공"""
        try:
            # index.html 파일 읽기
            with open('index.html', 'r', encoding='utf-8') as file:
                content = file.read()
            
            # HTTP 200 응답 헤더 전송
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content.encode('utf-8'))))
            self.end_headers()
            
            # HTML 내용 전송
            self.wfile.write(content.encode('utf-8'))
            
        except FileNotFoundError:
            # index.html 파일이 없는 경우 404 에러
            self.send_error(404, 'File not found: index.html')
        except Exception as e:
            # 기타 오류 처리
            self.send_error(500, f'Internal server error: {str(e)}')
    
    def log_access(self):
        """접속 정보를 서버 콘솔에 출력"""
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client_ip = self.client_address[0]
        
        print(f'[{current_time}] 접속 - IP: {client_ip}, 경로: {self.path}')
    

def start_server():
    """HTTP 서버 시작 - 포트 8080 고정"""
    port = 8080
    
    try:
        with socketserver.TCPServer(('', port), SpacePirateHandler) as httpd:
            print(f'우주 해적 웹서버가 포트 {port}에서 시작되었습니다.')
            print(f'웹 브라우저에서 http://localhost:{port} 로 접속하세요.')
            print('서버를 중지하려면 Ctrl+C를 누르세요.')
            print('-' * 50)
            
            # 서버 실행
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f'포트 {port}가 이미 사용 중입니다. 기존 프로세스를 종료하고 다시 시도하세요.')
        else:
            print(f'서버 시작 오류: {e}')
    except KeyboardInterrupt:
        print('\n서버가 사용자에 의해 중지되었습니다.')


if __name__ == '__main__':
    start_server()
