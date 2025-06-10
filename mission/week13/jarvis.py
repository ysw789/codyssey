import os
import csv
import sys

# STT 및 오디오 처리를 위한 외부 라이브러리 임포트
# pip install SpeechRecognition pydub
try:
    import speech_recognition as sr
    from pydub import AudioSegment
    from pydub.silence import detect_nonsilent
except ImportError:
    print('오류: 필수 라이브러리가 설치되지 않았습니다.')
    print('터미널에서 "pip install SpeechRecognition pydub" 명령어를 실행해주세요.')
    sys.exit(1)


def convert_to_wav_if_needed(file_path):
    """
    주어진 파일이 WAV 형식이 아닐 경우 WAV로 변환합니다.
    pydub은 FFmpeg이 설치되어 있어야 mp3 등 다양한 포맷을 처리할 수 있습니다.
    """
    path, extension = os.path.splitext(file_path)
    if extension.lower() != '.wav':
        wav_path = path + '.wav'
        print(f"'{file_path}' 파일을 '{wav_path}'(으)로 변환합니다...")
        try:
            sound = AudioSegment.from_file(file_path)
            sound.export(wav_path, format='wav')
            return wav_path
        except Exception as e:
            print(f"오류: '{file_path}' 파일 변환에 실패했습니다. FFmpeg이 설치되었는지 확인하세요.")
            print(f'세부 정보: {e}')
            return None
    return file_path


def format_timestamp(milliseconds):
    """밀리초를 'HH:MM:SS.ms' 형식의 문자열로 변환합니다."""
    total_seconds = milliseconds // 1000
    ms = milliseconds % 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    hours = minutes // 60
    minutes = minutes % 60
    return f'{hours:02}:{minutes:02}:{seconds:02}.{ms:03}'


def process_audio_file(audio_file_path):
    """음성 파일에서 텍스트를 추출하고 시간 정보와 함께 CSV로 저장합니다."""
    print(f"\n--- '{audio_file_path}' 파일 처리 시작 ---")

    # 1. 오디오 파일을 WAV 형식으로 준비
    wav_path = convert_to_wav_if_needed(audio_file_path)
    if not wav_path:
        return

    try:
        sound = AudioSegment.from_wav(wav_path)
    except Exception as e:
        print(f"오류: WAV 파일 로드에 실패했습니다. '{wav_path}', 오류: {e}")
        return

    # 2. 음성이 없는 부분을 기준으로 파일 분할
    # min_silence_len: 최소 침묵 길이 (밀리초)
    # silence_thresh: 침묵으로 간주할 소리 크기 (데시벨)
    try:
        nonsilent_data = detect_nonsilent(
            sound,
            min_silence_len=700,
            silence_thresh=sound.dBFS - 16,
            seek_step=1
        )
    except Exception as e:
        print(f"오류: 음성 구간 탐지 중 오류 발생: {e}")
        return

    if not nonsilent_data:
        print('음성 구간을 탐지하지 못했습니다. 파일이 비어있거나 너무 조용할 수 있습니다.')
        return

    print(f'총 {len(nonsilent_data)}개의 음성 구간을 감지했습니다.')

    # 3. 각 음성 구간을 텍스트로 변환
    recognizer = sr.Recognizer()
    results = []

    temp_chunk_dir = 'temp_audio_chunks'
    if not os.path.isdir(temp_chunk_dir):
        os.mkdir(temp_chunk_dir)

    for i, (start_ms, end_ms) in enumerate(nonsilent_data):
        audio_chunk = sound[start_ms:end_ms]
        chunk_filename = os.path.join(temp_chunk_dir, f'chunk_{i}.wav')
        audio_chunk.export(chunk_filename, format='wav')

        with sr.AudioFile(chunk_filename) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language='ko-KR')
                timestamp = format_timestamp(start_ms)
                results.append([timestamp, text])
                print(f'[{timestamp}] {text}')
            except sr.UnknownValueError:
                print(f'[{format_timestamp(start_ms)}] 음성을 인식할 수 없습니다.')
            except sr.RequestError as e:
                print(f'API 요청 오류: {e}')
                break  # API 오류 시 중단

    # 임시 파일 및 디렉터리 정리
    for f in os.listdir(temp_chunk_dir):
        os.remove(os.path.join(temp_chunk_dir, f))
    os.rmdir(temp_chunk_dir)

    # 4. 결과를 CSV 파일로 저장
    if results:
        csv_filename = os.path.splitext(audio_file_path)[0] + '.csv'
        try:
            with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['시간', '인식된 텍스트'])
                writer.writerows(results)
            print(f"성공: 결과가 '{csv_filename}'에 저장되었습니다.")
        except IOError as e:
            print(f"오류: CSV 파일 저장에 실패했습니다. 오류: {e}")
    else:
        print('변환된 텍스트가 없어 CSV 파일을 생성하지 않았습니다.')

    print(f"--- '{audio_file_path}' 파일 처리 완료 ---")


def search_keyword_in_csv(keyword):
    """현재 디렉터리의 CSV 파일에서 키워드를 검색합니다 (보너스 과제)."""
    print(f"\n>>> '{keyword}' 키워드 검색 시작...")
    found_count = 0
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]

    if not csv_files:
        print('검색할 CSV 파일이 없습니다.')
        return

    for filename in csv_files:
        try:
            with open(filename, mode='r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                next(reader, None)  # 헤더 건너뛰기
                for row in reader:
                    if len(row) >= 2 and keyword in row[1]:
                        print(f"  - 파일: {filename}, 시간: {row[0]}, 내용: {row[1]}")
                        found_count += 1
        except Exception as e:
            print(f"오류: '{filename}' 파일 읽기 중 오류 발생: {e}")

    if found_count == 0:
        print('해당 키워드를 포함하는 내용을 찾지 못했습니다.')

    print('<<< 키워드 검색 완료')


def main():
    """프로그램의 메인 로직을 실행합니다."""
    # 1. 음성 파일 처리
    audio_extensions = ('.wav', '.mp3', '.m4a', '.flac', '.ogg')
    records_dir = os.path.join(os.path.dirname(__file__), 'records')
    if not os.path.isdir(records_dir):
        print(f"'{records_dir}' 디렉터리가 존재하지 않습니다.")
        return

    audio_files = [os.path.join(records_dir, f)
                   for f in os.listdir(records_dir)
                   if f.lower().endswith(audio_extensions)]

    if not audio_files:
        print(f"'{records_dir}' 디렉터리에 처리할 음성 파일이 없습니다.")
    else:
        for audio_file in audio_files:
            process_audio_file(audio_file)

    # 2. 키워드 검색 (보너스 과제)
    while True:
        try:
            user_input = input('\nCSV 파일에서 검색할 키워드를 입력하세요 (종료하려면 그냥 엔터를 누르세요): ')
        except KeyboardInterrupt:
            print('\n프로그램을 종료합니다.')
            break

        if not user_input:
            print('프로그램을 종료합니다.')
            break
        search_keyword_in_csv(user_input)


if __name__ == '__main__':
    main()
