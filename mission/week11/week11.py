def caesar_cipher_decode(target_text):
    # 카이사르 암호 해독 함수: 입력된 텍스트를 1부터 26까지의 shift 값으로 해독 시도
    for shift in range(1, 27):
        decoded_text = ""
        # 각 문자를 순회하며 shift 값만큼 이동시켜 해독
        for char in target_text:
            if char.isalpha():
                # 알파벳인 경우 대문자와 소문자를 구분하여 처리
                ascii_base = ord('A') if char.isupper() else ord('a')
                # 현재 문자를 숫자로 변환 후 shift만큼 뒤로 이동 (해독)
                new_pos = (ord(char) - ascii_base - shift) % 26
                # 이동된 위치를 다시 문자로 변환
                decoded_text += chr(ascii_base + new_pos)
            else:
                # 알파벳이 아닌 경우 (공백, 특수문자 등) 그대로 유지
                decoded_text += char
        # 각 shift 값에 따른 해독 결과를 출력하여 사용자가 눈으로 확인 가능하도록 함
        print(f"Shift {shift}: {decoded_text}")

        # 보너스 과제: 사전에 있는 키워드가 해독된 텍스트에 있는지 확인
        simple_dictionary = ["the", "and", "is", "in", "it", "to", "that", "of", "for", "on"]
        decoded_words = decoded_text.lower().split()
        for word in decoded_words:
            if word in simple_dictionary:
                # 키워드가 발견되면 반복을 멈추고 결과를 반환
                print(f"Keyword '{word}' found at shift {shift}. Stopping decryption.")
                return decoded_text, shift

    # 키워드가 발견되지 않은 경우, 마지막 결과와 shift 값을 반환
    return decoded_text, shift


def main():
    # 파일 읽기: 암호화된 텍스트를 password.txt에서 가져옴
    try:
        with open("password.txt", "r") as file:
            # 파일 내용을 읽어 암호화된 텍스트 저장
            encrypted_text = file.read().strip()
            print(f"Encrypted text from file: {encrypted_text}")
    except FileNotFoundError:
        # 파일이 없는 경우 오류 메시지 출력 후 종료
        print("Error: password.txt file not found.")
        return
    except IOError:
        # 파일 읽기 중 오류 발생 시 메시지 출력 후 종료
        print("Error: An error occurred while reading the file.")
        return
    except Exception as e:
        # 기타 예외 발생 시 메시지 출력 후 종료
        print(f"Error: An unexpected error occurred: {e}")
        return

    # 카이사르 암호 해독 함수 호출: 모든 shift 값으로 해독 시도
    decoded_result, used_shift = caesar_cipher_decode(encrypted_text)

    # 사용자 입력: 사용자가 의미 있는 해독 결과를 확인한 후 적절한 shift 값을 입력
    try:
        user_shift = int(input("Enter the shift number where the cipher is decoded (1-26): "))
        if 1 <= user_shift <= 26:
            # 사용자가 선택한 shift 값으로 최종 해독 수행
            final_text = ""
            for char in encrypted_text:
                if char.isalpha():
                    ascii_base = ord('A') if char.isupper() else ord('a')
                    new_pos = (ord(char) - ascii_base - user_shift) % 26
                    final_text += chr(ascii_base + new_pos)
                else:
                    final_text += char
            # 최종 해독 결과를 result.txt 파일에 저장
            try:
                with open("result.txt", "w") as result_file:
                    result_file.write(final_text)
                print(f"Decoded text saved to result.txt with shift {user_shift}: {final_text}")
            except IOError:
                # 파일 쓰기 중 오류 발생 시 메시지 출력
                print("Error: An error occurred while writing to result.txt.")
            except Exception as e:
                # 기타 예외 발생 시 메시지 출력
                print(f"Error: An unexpected error occurred while saving: {e}")
        else:
            # 입력값이 유효 범위를 벗어난 경우 오류 메시지 출력
            print("Error: Shift value must be between 1 and 26.")
    except ValueError:
        # 숫자가 아닌 값을 입력한 경우 오류 메시지 출력
        print("Error: Please enter a valid number.")
    except Exception as e:
        # 기타 예외 발생 시 메시지 출력
        print(f"Error: An unexpected error occurred: {e}")


if __name__ == "__main__":
    # 프로그램의 진입점: main 함수를 호출하여 실행 시작
    main()
