import sys

def open_file(file_path):
    try:
        with open(file_path, 'r') as f:
            file = f.read()
            return file
    except FileNotFoundError:
        print(f'파일을 찾을 수 없습니다: {file_path}')
        sys.exit(1) # 오류로 인한 종료
    except PermissionError:
        print(f'파일을 열 권한이 없습니다: {file_path}')
        sys.exit(1)
    except UnicodeDecodeError:
        print(f'읽을 수 없는 형식입니다: {file_path}')
        sys.exit(1)
    except Exception as e:
        print(f'알 수 없는 에러가 발생했습니다: {e}')
        sys.exit(99) # 예상치 못한 오류

def write_into_markdown(file):
    lines = file.strip().split('\n')

    markdown_content = []
    markdown_content.append("## 미션 컴퓨터 로그 분석")
    markdown_content.append("")
    markdown_content.append("| 시간 | 이벤트 | 메시지 |")
    markdown_content.append("|------|--------|--------|")

    fatal_logs = []
    fatal_logs.append("## 산소 탱크 관련 로그 분석")
    fatal_logs.append("")
    fatal_logs.append("| 시간 | 이벤트 | 메시지 |")
    fatal_logs.append("|------|--------|--------|")
    
    data_lines = lines[1:]
    sorted_lines = sorted(data_lines, key=lambda x: x.split(',')[0], reverse=True)
    
    for line in sorted_lines:
        parts = line.strip().split(',', 2)
        
        timestamp = parts[0].strip()
        event = parts[1].strip()
        message = parts[2].strip()
        
        markdown_content.append(f"| {timestamp} | {event} | {message} |")

        if 'oxygen tank' in message.lower():
            fatal_logs.append(f"| {timestamp} | {event} | {message} |")
    
    with open('log_analysis.md', 'w') as md_file:
        md_file.write('\n'.join(markdown_content))

    with open('fatal_logs.md', 'w') as md_file:
        md_file.write('\n'.join(fatal_logs))

    print('>> Markdown 파일 생성 성공!')

file_path = 'mission_computer_main.log'
log_content = open_file(file_path)
write_into_markdown(log_content)
