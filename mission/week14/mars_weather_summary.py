import csv
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv


class MySQLHelper:
    def __init__(self, host, user, password, database, port):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            print('>> MySQL DB 연결 성공')
            return True
        except Error as e:
            print(f'>> MySQL 연결 오류: {e}')
            return False

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print('>> MySQL DB 연결 해제')

    def execute_query(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor
        except Error as e:
            print(f'>> 쿼리 실행 오류: {e}')
            return None

    def create_table(self, table_query):
        cursor = self.execute_query(table_query)
        if cursor:
            print('>> 테이블 생성 완료')
            cursor.close()
            return True
        return False

    def insert_data(self, insert_query, data):
        cursor = self.execute_query(insert_query, data)
        if cursor:
            cursor.close()
            return True
        return False


def read_csv_file(file_path):
    data = []
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            header = next(csv_reader)  # 헤더 스킵
            print(f'>> CSV 헤더: {header}')

            for row in csv_reader:
                data.append(row)

        print(f'>> CSV 파일에서 {len(data)}개의 데이터 행을 성공적으로 읽었습니다')

        return data
    except FileNotFoundError:
        print(f'>> 파일을 찾을 수 없습니다: {file_path}')
        return []
    except Exception as e:
        print(f'>> CSV 파일 읽기 오류: {e}')
        return []


def load_database_config():
    load_dotenv()
    return {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USERNAME'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME'),
        'port' : int(os.getenv('DB_PORT'))
    }


def main():
    print('=== Mars Weather Data Import System ===')

    db_config = load_database_config()

    mysql_helper = MySQLHelper(**db_config)

    if not mysql_helper.connect():
        print('>> 데이터베이스 연결에 실패했습니다.')
        return

    create_table_query = '''
         CREATE TABLE IF NOT EXISTS mars_weather \
         ( \
             weather_id INT AUTO_INCREMENT PRIMARY KEY, \
             mars_date DATE NOT NULL, \
             temp DECIMAL, \
             storm INT
         ) \
    '''

    if not mysql_helper.create_table(create_table_query):
        print('>> 테이블 생성에 실패했습니다.')
        mysql_helper.disconnect()
        return

    csv_file_path = 'mars_weathers_data.csv'
    csv_data = read_csv_file(csv_file_path)

    if not csv_data:
        print('>> 삽입할 데이터가 없습니다.')
        mysql_helper.disconnect()
        return

    insert_query = '''
       INSERT INTO mars_weather (mars_date, temp, storm)
       VALUES (%s, %s, %s) \
    '''

    successful_inserts = 0
    failed_inserts = 0

    print(f'\n>> {len(csv_data)}개의 데이터를 데이터베이스에 삽입 중...')

    for i, row in enumerate(csv_data, 1):
        try:
            # CSV 데이터: weather_id, mars_date, temp, storm
            # weather_id는 AUTO_INCREMENT이므로 제외하고 나머지 3개 컬럼만 사용
            mars_date = row[1]
            temp = float(row[2])
            storm = int(row[3])

            if mysql_helper.insert_data(insert_query, (mars_date, temp, storm)):
                successful_inserts += 1
            else:
                failed_inserts += 1
                print(f'>> 데이터 삽입 실패 (행 {i}): {row}')

        except (ValueError, IndexError) as e:
            failed_inserts += 1
            print(f'>> 데이터 처리 오류 (행 {i}): {e}, 데이터: {row}')
            continue

    print(f'\n=== 데이터 삽입 완료 ===')
    print(f'성공: {successful_inserts}개')
    print(f'실패: {failed_inserts}개')
    print(f'총 처리: {len(csv_data)}개')

    mysql_helper.disconnect()
    print('\n>> 작업 수행 완료')


if __name__ == '__main__':
    main()
