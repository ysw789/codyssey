INVENTORY_LIST_FILE_NAME = 'Mars_Base_Inventory_List.csv'

def parse_csv_to_list(file_path):
    data_list = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            
            for index, line in enumerate(f):
                if index == 0:
                    continue  # 첫 번째 줄은 건너뜀
                
                row_data = line.strip().split(',')
                row_data = [field.strip() for field in row_data]
                data_list.append(row_data)

            return data_list

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
    list = parse_csv_to_list(INVENTORY_LIST_FILE_NAME)
    for i in list:
        print(i)
