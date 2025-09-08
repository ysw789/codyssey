import os
import datetime
import glob
import queue
import threading
import time
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np


class VoiceRecorder:
    """음성 녹음 및 관리를 위한 클래스"""

    def __init__(self):
        self.sample_rate = 44100
        self.channels = 1
        self.dtype = 'float32'
        self.records_dir = 'records'
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self._create_records_directory()

    def _create_records_directory(self):
        """records 디렉토리 생성"""
        if not os.path.exists(self.records_dir):
            os.makedirs(self.records_dir)

    def _generate_filename(self):
        """현재 날짜와 시간을 기반으로 파일명 생성"""
        now = datetime.datetime.now()
        timestamp = now.strftime('%Y%m%d-%H%M%S')
        filename = f'{timestamp}.wav'
        return os.path.join(self.records_dir, filename)

    def _audio_callback(self, indata, frames, time, status):
        """오디오 스트림 콜백 함수"""
        if self.is_recording:
            self.audio_queue.put(indata.copy())

    def record_audio(self):
        """음성 녹음 및 저장 (Enter 키 입력 시 종료, 최대 60초 제한)"""
        try:
            print('녹음을 시작합니다. 최대 60초 동안 녹음됩니다. Enter 키를 누르면 녹음이 종료됩니다...')

            # 녹음 상태 초기화
            self.is_recording = True
            self.audio_queue = queue.Queue()

            # Enter 키 입력을 감지하는 스레드
            def wait_for_enter():
                input()
                self.is_recording = False

            input_thread = threading.Thread(target=wait_for_enter)
            input_thread.daemon = True
            input_thread.start()

            # 오디오 스트림 시작 (기본 마이크 사용)
            with sd.InputStream(
                    callback=self._audio_callback,
                    channels=self.channels,
                    samplerate=self.sample_rate,
                    dtype=self.dtype
            ):
                print('녹음 중... Enter 키를 눌러 종료')

                # 녹음 시작 시간 기록
                start_time = time.time()

                # 주기적으로 상태 체크 (0.1초마다)
                while self.is_recording:
                    time.sleep(0.1)

                    # 60초 경과 시 자동 종료
                    if time.time() - start_time >= 60:
                        print('\n최대 녹음 시간 60초에 도달하여 녹음을 종료합니다.')
                        self.is_recording = False
                        break

                print('녹음을 종료합니다...')

            # 큐에서 오디오 데이터 수집
            audio_data = []
            while not self.audio_queue.empty():
                audio_data.append(self.audio_queue.get())

            if audio_data:
                # 오디오 데이터 합치기
                recording = np.concatenate(audio_data, axis=0)

                # WAV 파일 저장을 위해 int16으로 변환
                recording_int16 = (recording * 32767).astype(np.int16)

                # 파일 저장
                filename = self._generate_filename()
                write(filename, self.sample_rate, recording_int16)

                print(f'녹음이 완료되었습니다: {filename}')
                print(f'녹음 시간: {len(recording) / self.sample_rate:.2f}초')
                return filename
            else:
                print('녹음된 데이터가 없습니다.')
                return None

        except Exception as e:
            print(f'녹음 중 오류가 발생했습니다: {e}')
            self.is_recording = False
            return None

    def show_recordings_by_date_range(self, start_date, end_date):
        """특정 날짜 범위의 녹음 파일 조회"""
        try:
            # 날짜 문자열을 datetime 객체로 변환
            start_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
            end_dt = datetime.datetime.strptime(end_date, '%Y%m%d')

            # records 폴더의 모든 WAV 파일 검색
            pattern = os.path.join(self.records_dir, '*.wav')
            files = glob.glob(pattern)

            matching_files = []

            for file_path in files:
                filename = os.path.basename(file_path)
                date_part = filename.split('-')[0]

                try:
                    file_date = datetime.datetime.strptime(date_part, '%Y%m%d')
                    if start_dt <= file_date <= end_dt:
                        matching_files.append(file_path)
                except ValueError:
                    continue

            # 결과 출력
            if matching_files:
                print(f'{start_date}부터 {end_date}까지의 녹음 파일:')
                for file_path in sorted(matching_files):
                    filename = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path)
                    print(f'  {filename} ({file_size} bytes)')
            else:
                print('해당 날짜 범위에 녹음 파일이 없습니다.')

        except ValueError:
            print('날짜 형식이 올바르지 않습니다. YYYYMMDD 형식으로 입력해주세요.')
        except Exception as e:
            print(f'파일 검색 중 오류가 발생했습니다: {e}')


def main():
    """메인 함수"""
    recorder = VoiceRecorder()

    while True:
        print('\n=== Jarvis 음성 녹음 시스템 ===')
        print('1. 음성 녹음 (Enter로 종료, 최대 60초)')
        print('2. 날짜 범위별 녹음 파일 조회')
        print('3. 종료')

        choice = input('메뉴를 선택하세요 (1-3): ').strip()

        if choice == '1':
            recorder.record_audio()

        elif choice == '2':
            start_date = input('시작 날짜 (YYYYMMDD): ').strip()
            end_date = input('끝 날짜 (YYYYMMDD): ').strip()
            recorder.show_recordings_by_date_range(start_date, end_date)

        elif choice == '3':
            print('프로그램을 종료합니다.')
            break

        else:
            print('올바른 메뉴를 선택해주세요.')


if __name__ == '__main__':
    main()
