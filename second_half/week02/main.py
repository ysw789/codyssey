import socket
import threading

# 서버 설정
HOST = '127.0.0.1'
PORT = 12345

# 클라이언트 목록
clients = []
nicknames = []

# 스레드 동기화를 위한 락
client_lock = threading.Lock()


def handle_client(client):
    """클라이언트로부터 메시지를 수신하고 브로드캐스트하는 함수"""
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == '/종료':
                with client_lock:
                    index = clients.index(client)
                    clients.remove(client)
                    nickname = nicknames[index]
                    nicknames.remove(nickname)
                client.close()
                broadcast(f'{nickname}님이 퇴장하셨습니다.'.encode('utf-8'))
                break
            elif message.startswith('@'):
                # 귓속말 기능
                parts = message.split(' ', 1)
                if len(parts) >= 2:
                    target_nickname = parts[0][1:]  # @ 제거
                    private_message = parts[1]
                    with client_lock:
                        if target_nickname in nicknames:
                            target_index = nicknames.index(target_nickname)
                            target_client = clients[target_index]
                            sender_index = clients.index(client)
                            sender_nickname = nicknames[sender_index]
                        else:
                            target_client = None
                            sender_nickname = None
                    
                    if target_client and sender_nickname:
                        whisper_message = f'[귓속말] {sender_nickname}> {private_message}'
                        target_client.send(whisper_message.encode('utf-8'))
                        # 발신자에게도 귓속말 전송 확인 메시지
                        client.send(f'[귓속말 전송] {target_nickname}에게: {private_message}'.encode('utf-8'))
                    else:
                        client.send('해당 닉네임의 사용자가 없습니다.'.encode('utf-8'))
            else:
                # 일반 메시지
                with client_lock:
                    index = clients.index(client)
                    nickname = nicknames[index]
                broadcast(f'{nickname}> {message}'.encode('utf-8'))
        except:
            # 클라이언트 연결이 끊어진 경우
            with client_lock:
                index = clients.index(client)
                clients.remove(client)
                nickname = nicknames[index]
                nicknames.remove(nickname)
            client.close()
            broadcast(f'{nickname}님이 퇴장하셨습니다.'.encode('utf-8'))
            break


def broadcast(message):
    """모든 클라이언트에게 메시지를 전송하는 함수"""
    with client_lock:
        clients_copy = clients.copy()
    
    # 락 해제 후 메시지 전송
    for client in clients_copy:
        try:
            client.send(message)
        except:
            # 전송 실패한 클라이언트 제거
            with client_lock:
                if client in clients:
                    index = clients.index(client)
                    clients.remove(client)
                    nicknames.pop(index)


def start_server():
    """서버 시작 함수"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()

    print(f'서버가 {HOST}:{PORT}에서 실행 중입니다.')
    print('클라이언트 연결을 기다리는 중...')

    while True:
        client, address = server.accept()
        print(f'새로운 연결: {address}')

        client.send('닉네임을 입력하세요: '.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        
        with client_lock:
            nicknames.append(nickname)
            clients.append(client)

        print(f'닉네임: {nickname}')
        broadcast(f'{nickname}님이 입장하셨습니다.'.encode('utf-8'))
        client.send('서버에 연결되었습니다.'.encode('utf-8'))

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()


def start_client():
    """클라이언트 시작 함수"""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    nickname = input('닉네임을 입력하세요: ')
    client.send(nickname.encode('utf-8'))

    def receive():
        """메시지 수신 함수"""
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if message == '닉네임을 입력하세요: ':
                    client.send(nickname.encode('utf-8'))
                else:
                    print(message)
            except:
                print('서버와의 연결이 종료되었습니다.')
                client.close()
                break

    def write():
        """메시지 전송 함수"""
        while True:
            message = input('')
            if message == '/종료':
                client.send('/종료'.encode('utf-8'))
                client.close()
                break
            else:
                client.send(message.encode('utf-8'))

    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()


if __name__ == '__main__':
    choice = input('서버를 시작하려면 1, 클라이언트를 시작하려면 2를 입력하세요: ')
    if choice == '1':
        start_server()
    elif choice == '2':
        start_client()
    else:
        print('잘못된 선택입니다. 1 또는 2를 입력하세요.')
