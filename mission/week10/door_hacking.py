import zipfile
import itertools
import string
import time
import multiprocessing
import os
import math


def try_password(zip_file, password_str):
    """ZIP 파일에 대해 주어진 암호를 시도합니다."""
    try:
        zip_file.extractall(pwd=password_str.encode())
        return True
    except:
        return False


def worker(task_queue, chars, zip_path, result_queue, counter, start_time, total_combinations):
    """워커 프로세스의 작업을 정의합니다."""
    zip_file = zipfile.ZipFile(zip_path)
    local_counter = 0
    last_log_time = start_time

    while True:
        try:
            # 작업 가져오기
            prefix = task_queue.get(timeout=1)
            if prefix is None:  # 작업 종료 신호
                break

            # 나머지 자리 조합 생성
            remaining_len = 8 - len(prefix)

            for password_tuple in itertools.product(chars, repeat=remaining_len):
                local_counter += 1

                # 전체 암호 생성
                password = prefix + ''.join(password_tuple)

                # 30초마다 진행 상황 출력
                current_time = time.time()
                if current_time - last_log_time >= 30:
                    with counter.get_lock():
                        counter.value += local_counter
                        local_counter = 0

                    elapsed = current_time - start_time
                    progress = (counter.value / total_combinations) * 100
                    print(f"경과 시간: {elapsed:.2f}초, 진행도: {progress:.4f}%")
                    last_log_time = current_time

                # 암호 시도
                if try_password(zip_file, password):
                    with counter.get_lock():
                        counter.value += local_counter
                    result_queue.put(password)
                    return

        except multiprocessing.queues.Empty:
            break

    # 나머지 카운터 값 업데이트
    with counter.get_lock():
        counter.value += local_counter


def unlock_zip(zip_path="./emergency_storage_key.zip"):
    """ZIP 파일의 암호를 찾는 함수입니다."""
    print(f"[*] {zip_path} 파일의 암호 풀기 시작...")

    # 사용 가능한 코어 수 확인 및 출력
    num_processes = multiprocessing.cpu_count()
    print(f"[*] 사용 가능한 코어 수: {num_processes}")

    # 시작 시간 기록
    start_time = time.time()

    # 가능한 문자 집합
    chars = string.digits + string.ascii_lowercase  # 0-9 + a-z
    total_combinations = len(chars) ** 8  # 8자리 비밀번호

    print(f"[*] 가능한 조합 수: {total_combinations:,}")
    print(f"[*] 병렬 처리 시작...")

    # 멀티프로세싱 설정
    manager = multiprocessing.Manager()
    result_queue = manager.Queue()
    task_queue = manager.Queue()
    counter = multiprocessing.Value('i', 0)

    # 작업 큐 준비 - 첫 3글자 기반으로 작업 분배
    # 작업 큐 크기를 최적화하기 위해 적절한 청크 크기 계산
    chunk_size = max(1, math.ceil((len(chars) ** 3) / (num_processes * 10)))
    chunks = 0

    for first_three in itertools.product(chars, repeat=3):
        prefix = ''.join(first_three)
        if chunks % chunk_size == 0:
            task_queue.put(prefix)
        chunks += 1

    # 프로세스 시작
    processes = []
    for _ in range(num_processes):
        p = multiprocessing.Process(
            target=worker,
            args=(task_queue, chars, zip_path, result_queue, counter, start_time, total_combinations)
        )
        processes.append(p)
        p.start()

    # 결과 대기
    found_password = None
    try:
        while any(p.is_alive() for p in processes):
            if not result_queue.empty():
                found_password = result_queue.get()
                # 모든 프로세스 종료
                for p in processes:
                    p.terminate()
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[!] 사용자에 의해 중단되었습니다.")
        for p in processes:
            p.terminate()

    # 결과 정리
    for p in processes:
        p.join()

    elapsed_time = time.time() - start_time

    if found_password:
        print(f"[+] 암호 발견: {found_password}")
        print(f"[+] 소요 시간: {elapsed_time:.2f}초")
        print(f"[+] 시도 횟수: {counter.value:,}")

        # 암호를 파일에 저장
        with open("password.txt", "w") as f:
            f.write(found_password)
        print(f"[+] 암호가 password.txt 파일에 저장되었습니다.")

        return found_password
    else:
        print(f"[-] 암호를 찾지 못했습니다.")
        print(f"[-] 소요 시간: {elapsed_time:.2f}초")
        print(f"[-] 시도 횟수: {counter.value:,}")

        return None


if __name__ == "__main__":
    unlock_zip()
