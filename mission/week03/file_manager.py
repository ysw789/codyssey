class FileManager:
    def __init__(self, csv_file, binary_file, filtered_csv_file):
        self.csv_file = csv_file
        self.binary_file = binary_file
        self.filtered_csv_file = filtered_csv_file

    def parse_csv_to_list(self):
        # CSV 파일을 읽어 헤더와 데이터 리스트를 반환
        data_list = []
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                headers = [field.strip() for field in first_line.strip().split(',')]
                for line in f:
                    row_data = line.strip().split(',')
                    row_data = [field.strip() for field in row_data]
                    data_list.append(row_data)
            return headers, data_list
        except FileNotFoundError:
            print(f'파일을 찾을 수 없습니다: {self.csv_file}')
            exit(1)
        except PermissionError:
            print(f'파일을 열 권한이 없습니다: {self.csv_file}')
            exit(1)
        except UnicodeDecodeError:
            print(f'읽을 수 없는 형식입니다: {self.csv_file}')
            exit(1)
        except Exception as e:
            print(f'알 수 없는 에러가 발생했습니다: {e}')
            exit(99)

    def write_into_binary_file(self, data):
        # 정렬된 데이터를 이진 파일에 저장
        try:
            with open(self.binary_file, 'wb') as bin_file:
                bin_file.write(bytes(str(data), 'utf-8'))
            print('>> 바이너리 파일이 저장되었습니다.')
        except Exception as e:
            print(f'>> 바이너리 파일 저장 중 오류 발생: {e}')
            exit(1)

    def write_into_csv_file(self, headers, filtered_rows):
        # 필터링 된 데이터를 CSV 파일로 저장
        try:
            with open(self.filtered_csv_file, 'w', encoding='utf-8') as f_out:
                f_out.write(','.join(headers) + '\n')
                for row in filtered_rows:
                    f_out.write(','.join(row) + '\n')
            print('>> 필터링 된 CSV 파일이 저장되었습니다.')
        except Exception as e:
            print(f'CSV 파일 저장 중 오류 발생: {e}')
            exit(1)

    def read_and_print_binary_file(self, file_path):
        # 저장된 이진 파일을 읽어 원본 문자열 그대로 출력
        try:
            with open(file_path, 'rb') as bin_file:
                binary_data = bin_file.read()
                inventory_str = binary_data.decode('utf-8')
                print('>> 바이너리 파일')
                print(inventory_str)
        except Exception as e:
            print(f'>> 바이너리 파일 읽기 중 오류 발생: {e}')
            exit(1)
