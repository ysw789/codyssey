import smtplib
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

# 스크립트와 같은 디렉터리의 CSV 경로 고정
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV_PATH = os.path.join(SCRIPT_DIR, 'mail_target_list.csv')


def send_html_email(sender_email, receiver_email, password, subject, html_body, plain_body=None):
    """
    HTML 형식의 이메일을 전송합니다.
    
    Args:
        sender_email (str): 발신자 이메일 주소
        receiver_email (str): 수신자 이메일 주소
        password (str): 발신자 이메일 비밀번호 또는 앱 비밀번호
        subject (str): 이메일 제목
        html_body (str): HTML 형식의 이메일 본문
        plain_body (str): 일반 텍스트 형식의 이메일 본문 (선택사항)
    """
    # Gmail SMTP 서버 설정
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    
    # 이메일 메시지 구성
    message = MIMEMultipart('alternative')
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject
    
    # 일반 텍스트 버전 추가 (HTML을 지원하지 않는 클라이언트용)
    if plain_body:
        text_part = MIMEText(plain_body, 'plain', 'utf-8')
        message.attach(text_part)
    
    # HTML 버전 추가
    html_part = MIMEText(html_body, 'html', 'utf-8')
    message.attach(html_part)
    
    try:
        # SMTP 서버 연결 및 이메일 전송
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # TLS 암호화 시작
            server.login(sender_email, password)
            text = message.as_string()
            server.sendmail(sender_email, receiver_email, text)
            print(f'HTML 이메일이 성공적으로 발송되었습니다! (수신자: {receiver_email})')
            return True
            
    except smtplib.SMTPAuthenticationError:
        print('인증 오류: 이메일 주소나 비밀번호를 확인하세요.')
        print('Gmail의 경우 앱 비밀번호를 사용해야 할 수 있습니다.')
        return False
    except smtplib.SMTPConnectError:
        print('연결 오류: SMTP 서버에 연결할 수 없습니다.')
        print('인터넷 연결을 확인하세요.')
        return False
    except smtplib.SMTPRecipientsRefused:
        print(f'수신자 오류: 수신자 이메일 주소가 잘못되었습니다. ({receiver_email})')
        return False
    except smtplib.SMTPServerDisconnected:
        print('서버 연결 끊김: SMTP 서버와의 연결이 끊어졌습니다.')
        return False
    except smtplib.SMTPException as e:
        print(f'SMTP 오류 발생: {e}')
        return False
    except Exception as e:
        print(f'예기치 않은 오류 발생: {e}')
        return False


def send_bulk_email_individual(sender_email, password, subject, html_body, plain_body, csv_file_path):
    """
    CSV 파일의 수신자들에게 개별적으로 이메일을 전송합니다.
    
    Args:
        sender_email (str): 발신자 이메일 주소
        password (str): 발신자 이메일 비밀번호 또는 앱 비밀번호
        subject (str): 이메일 제목
        html_body (str): HTML 형식의 이메일 본문
        plain_body (str): 일반 텍스트 형식의 이메일 본문
        csv_file_path (str): 수신자 목록이 담긴 CSV 파일 경로
    """
    recipients = read_recipients_from_csv(csv_file_path)
    if not recipients:
        return
    
    success_count = 0
    total_count = len(recipients)
    
    print(f'총 {total_count}명에게 개별 이메일을 발송합니다...')
    print('=' * 50)
    
    for name, email in recipients:
        print(f'발송 중: {name} ({email})')
        if send_html_email(sender_email, email, password, subject, html_body, plain_body):
            success_count += 1
        print('-' * 30)
    
    print(f'발송 완료: {success_count}/{total_count}명에게 성공적으로 발송되었습니다.')


def send_bulk_email_cc(sender_email, password, subject, html_body, plain_body, csv_file_path):
    """
    CSV 파일의 수신자들에게 CC로 이메일을 전송합니다.
    
    Args:
        sender_email (str): 발신자 이메일 주소
        password (str): 발신자 이메일 비밀번호 또는 앱 비밀번호
        subject (str): 이메일 제목
        html_body (str): HTML 형식의 이메일 본문
        plain_body (str): 일반 텍스트 형식의 이메일 본문
        csv_file_path (str): 수신자 목록이 담긴 CSV 파일 경로
    """
    recipients = read_recipients_from_csv(csv_file_path)
    if not recipients:
        return
    
    # Gmail SMTP 서버 설정
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    
    # 이메일 메시지 구성
    message = MIMEMultipart('alternative')
    message['From'] = sender_email
    message['Subject'] = subject
    
    # 수신자 이메일 주소 추출
    recipient_emails = [email for name, email in recipients]
    
    # 첫 번째 수신자를 To로, 나머지를 CC로 설정
    if recipient_emails:
        message['To'] = recipient_emails[0]
        if len(recipient_emails) > 1:
            message['Cc'] = ', '.join(recipient_emails[1:])
    
    # 일반 텍스트 버전 추가
    if plain_body:
        text_part = MIMEText(plain_body, 'plain', 'utf-8')
        message.attach(text_part)
    
    # HTML 버전 추가
    html_part = MIMEText(html_body, 'html', 'utf-8')
    message.attach(html_part)
    
    try:
        # SMTP 서버 연결 및 이메일 전송
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # TLS 암호화 시작
            server.login(sender_email, password)
            text = message.as_string()
            server.sendmail(sender_email, recipient_emails, text)
            print(f'CC 이메일이 성공적으로 발송되었습니다! (수신자: {len(recipient_emails)}명)')
            print(f'수신자 목록: {", ".join(recipient_emails)}')
            return True
            
    except smtplib.SMTPAuthenticationError:
        print('인증 오류: 이메일 주소나 비밀번호를 확인하세요.')
        print('Gmail의 경우 앱 비밀번호를 사용해야 할 수 있습니다.')
        return False
    except smtplib.SMTPConnectError:
        print('연결 오류: SMTP 서버에 연결할 수 없습니다.')
        print('인터넷 연결을 확인하세요.')
        return False
    except smtplib.SMTPRecipientsRefused:
        print('수신자 오류: 수신자 이메일 주소가 잘못되었습니다.')
        return False
    except smtplib.SMTPServerDisconnected:
        print('서버 연결 끊김: SMTP 서버와의 연결이 끊어졌습니다.')
        return False
    except smtplib.SMTPException as e:
        print(f'SMTP 오류 발생: {e}')
        return False
    except Exception as e:
        print(f'예기치 않은 오류 발생: {e}')
        return False


def read_recipients_from_csv(csv_file_path):
    """
    CSV 파일에서 수신자 목록을 읽어옵니다.
    
    Args:
        csv_file_path (str): CSV 파일 경로
        
    Returns:
        list: (이름, 이메일) 튜플의 리스트
    """
    recipients = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            
            # 헤더 행 건너뛰기
            next(reader, None)
            
            for row_num, row in enumerate(reader, start=2):
                if len(row) >= 2:
                    name = row[0].strip()
                    email = row[1].strip()
                    
                    if name and email:
                        recipients.append((name, email))
                    else:
                        print(f'경고: {row_num}번째 행에 빈 이름 또는 이메일이 있습니다.')
                else:
                    print(f'경고: {row_num}번째 행의 형식이 올바르지 않습니다.')
        
        print(f'CSV 파일에서 {len(recipients)}명의 수신자를 읽었습니다.')
        return recipients
        
    except FileNotFoundError:
        print(f'오류: CSV 파일을 찾을 수 없습니다: {csv_file_path}')
        return []
    except Exception as e:
        print(f'CSV 파일 읽기 오류: {e}')
        return []


def create_sample_csv():
    """
    샘플 CSV 파일을 생성합니다.
    """
    sample_data = [
        ['이름', '이메일'],
        ['김철수', 'kim@example.com'],
        ['이영희', 'lee@example.com'],
        ['박민수', 'park@example.com']
    ]
    
    with open(DEFAULT_CSV_PATH, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(sample_data)
    
    print(f'샘플 CSV 파일이 생성되었습니다: {DEFAULT_CSV_PATH}')


def main():
    """
    사용자 입력을 받아 HTML 이메일을 전송합니다.
    """
    print('=== HTML 이메일 대량 발송 프로그램 ===')
    print()
    
    # 사용자 입력 받기
    sender_email = input('발신자 이메일 주소를 입력하세요: ')
    password = input('발신자 이메일 비밀번호(또는 앱 비밀번호)를 입력하세요: ')
    subject = input('이메일 제목을 입력하세요: ')
    
    print('\nHTML 이메일 본문을 입력하세요 (여러 줄 입력 가능, 빈 줄로 종료):')
    html_lines = []
    while True:
        line = input()
        if line == '':
            break
        html_lines.append(line)
    
    html_body = '\n'.join(html_lines)
    
    # 일반 텍스트 버전 입력 (선택사항)
    print('\n일반 텍스트 버전을 입력하세요 (선택사항, 빈 줄로 건너뛰기):')
    plain_lines = []
    while True:
        line = input()
        if line == '':
            break
        plain_lines.append(line)
    
    plain_body = '\n'.join(plain_lines) if plain_lines else None
    
    # 같은 디렉터리의 CSV 파일 사용
    csv_file_path = DEFAULT_CSV_PATH
    if not os.path.exists(csv_file_path):
        print(f'CSV 파일이 존재하지 않습니다: {csv_file_path}')
        print('샘플 CSV 파일을 생성합니다...')
        create_sample_csv()
    
    # 발송 방법 선택
    print('\n발송 방법을 선택하세요:')
    print('1. 개별 발송 (각 수신자에게 개별적으로 발송)')
    print('2. CC 발송 (모든 수신자를 CC로 한 번에 발송)')
    
    while True:
        choice = input('선택 (1 또는 2): ').strip()
        if choice in ['1', '2']:
            break
        else:
            print('올바른 번호를 입력해주세요 (1 또는 2)')
    
    print('\n' + '=' * 50)
    
    if choice == '1':
        print('개별 발송을 시작합니다...')
        send_bulk_email_individual(sender_email, password, subject, html_body, plain_body, csv_file_path)
    else:
        print('CC 발송을 시작합니다...')
        send_bulk_email_cc(sender_email, password, subject, html_body, plain_body, csv_file_path)


if __name__ == '__main__':
    main()
