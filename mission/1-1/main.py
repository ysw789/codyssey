def open_file(file_path):
    with open(file_path, 'r') as f:
        file = f.read()
        return file

def write_into_markdown(file):
    lines = file.strip().split('\n')
    markdown_content = []
    
    markdown_content.append("## 미션 컴퓨터 로그 분석")
    markdown_content.append("")
    
    markdown_content.append("| 시간 | 이벤트 | 메시지 |")
    markdown_content.append("|------|--------|--------|")
    
    data_lines = lines[1:]
    
    sorted_lines = sorted(data_lines, key=lambda x: x.split(',')[0], reverse=True)
    
    for line in sorted_lines:
        parts = line.strip().split(',', 2)
        
        timestamp = parts[0].strip()
        event = parts[1].strip()
        message = parts[2].strip()
        
        markdown_content.append(f"| {timestamp} | {event} | {message} |")
    
    with open('log_analysis.md', 'w') as md_file:
        md_file.write('\n'.join(markdown_content))

file_path = 'mission_computer_main.log'
log_content = open_file(file_path)
write_into_markdown(log_content)
