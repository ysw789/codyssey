import zipfile
import itertools
import string
import time
import multiprocessing
import os


def try_password(zip_file, password_str):
    """ZIP 파일에 대해 주어진 암호를 시도합니다."""
    try:
        zip_file.extractall(pwd=password_str.encode())
        return True
    except:
        return False


def worker(process_id, num_processes, chars, zip_path, result_queue, counter, start_time):
    """워커 프로세스의 작업을 정의합니다."""
    zip_file = zipfile.ZipFile(zip_path)
    local_counter = 0

    # 각 프로세스는 시작 문자에 따라 작업을 나눔
    for i in range(process_id, len(chars), num_processes):
        first_char = chars[i]
        # 나머지 5자리 조합 생성
        for password_tuple in itertools.product(chars, repeat=5):
            local_counter += 1

            # 전체 암호 생성
            password = first_char + ''.join(password_tuple)

            # 1000번째 시도마다 진행 상황 출력
            if local_counter % 1000 == 0:
                with counter.get_lock():
                    counter.value += 1000
                elapsed = time.time() - start_time
                print(f"시도 횟수: {counter.value}, 경과 시간: {elapsed:.2f}초, 현재 암호: {password}")

            # 암호 시도
            if try_password(zip_file, password):
                result_queue.put(password)
                return

    # 나머지 카운터 값 업데이트
    with counter.get_lock():
        counter.value += local_counter % 1000


def unlock_zip(zip_path="./emergency_storage_key.zip"):
    """ZIP 파일의 암호를 찾는 함수입니다."""
    print(f"[*] {zip_path} 파일의 암호 풀기 시작...")

    # 시작 시간 기록
    start_time = time.time()

    # 가능한 문자 집합
    chars = string.digits + string.ascii_lowercase  # 0-9 + a-z
    total_combinations = len(chars) ** 6

    print(f"[*] 가능한 조합 수: {total_combinations}")
    print(f"[*] 병렬 처리 시작...")

    # 멀티프로세싱 설정
    num_processes = multiprocessing.cpu_count()
    manager = multiprocessing.Manager()
    result_queue = manager.Queue()
    counter = multiprocessing.Value('i', 0)

    # 프로세스 시작
    processes = []
    for i in range(num_processes):
        p = multiprocessing.Process(
            target=worker,
            args=(i, num_processes, chars, zip_path, result_queue, counter, start_time)
        )
        processes.append(p)
        p.start()

    # 결과 대기
    found_password = None
    while any(p.is_alive() for p in processes):
        if not result_queue.empty():
            found_password = result_queue.get()
            # 모든 프로세스 종료
            for p in processes:
                p.terminate()
            break
        time.sleep(0.1)

    # 결과 정리
    for p in processes:
        p.join()

    elapsed_time = time.time() - start_time

    if found_password:
        print(f"[+] 암호 발견: {found_password}")
        print(f"[+] 소요 시간: {elapsed_time:.2f}초")
        print(f"[+] 시도 횟수: {counter.value}")

        # 암호를 파일에 저장
        with open("password.txt", "w") as f:
            f.write(found_password)
        print(f"[+] 암호가 password.txt 파일에 저장되었습니다.")

        return found_password
    else:
        print(f"[-] 암호를 찾지 못했습니다.")
        print(f"[-] 소요 시간: {elapsed_time:.2f}초")
        print(f"[-] 시도 횟수: {counter.value}")

        return None


if __name__ == "__main__":
    unlock_zip()
