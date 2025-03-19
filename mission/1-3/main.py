INVENTORY_LIST_FILE_NAME = 'Mars_Base_Inventory_List.csv'
FILTERED_CSV_FILE_NAME = 'Mars_Base_Inventory_danger.csv'

def parse_csv_to_list(file_path):
    data_list = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            headers = [filed.strip() for filed in first_line.strip().split(',')]
            
            for index, line in enumerate(f):
                if index == 0:
                    continue  # 첫 번째 줄은 건너뜀
                
                row_data = line.strip().split(',')
                row_data = [field.strip() for field in row_data]
                data_list.append(row_data)

            return headers, data_list

    except FileNotFoundError:
        print(f'파일을 찾을 수 없습니다: {file_path}')
        exit(1)
    except PermissionError:
        print(f'파일을 열 권한이 없습니다: {file_path}')
        exit(1)
    except UnicodeDecodeError:
        print(f'읽을 수 없는 형식입니다: {file_path}')
        exit(1)
    except Exception as e:
        print(f'알 수 없는 에러가 발생했습니다: {e}')
        exit(99)

if __name__ == "__main__":
    headers, list = parse_csv_to_list(INVENTORY_LIST_FILE_NAME)
    
    flammability_index = headers.index('Flammability')
    if flammability_index == -1:
        print('Flammability 헤더를 찾을 수 없습니다.')
        exit(1)

    list = sorted(list, key=lambda x: float(x[flammability_index]), reverse=True)

    filtered_rows = [row for row in list if float(row[flammability_index]) >= 0.7]

    print('>> Flammability over 0.7')
    print(', '.join(headers))
    for row in filtered_rows:
        print(', '.join(row))

    try:
        with open(FILTERED_CSV_FILE_NAME, 'w', encoding='utf-8') as f_out:
            f_out.write(",".join(headers) + "\n")
            for row in filtered_rows:
                f_out.write(",".join(row) + "\n")
        print('>> 필터링 된 CSV 파일이 저장되었습니다.')
    except Exception as e:
        print(f"CSV 파일 저장 중 오류 발생: {e}")
        exit(1)