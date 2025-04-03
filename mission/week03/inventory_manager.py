class InventoryManager:
    def __init__(self, headers, data_list):
        self.headers = headers
        self.data_list = data_list
        self.flammability_index = self.get_flammability_index()

    def get_flammability_index(self):
        try:
            return self.headers.index('Flammability')
        except ValueError:
            print('>> Flammability 헤더를 찾을 수 없습니다.')
            exit(1)

    def sort_by_flammability_desc(self):
        # 데이터 리스트를 Flammability 값을 기준으로 내림차순 정렬
        self.data_list = sorted(
            self.data_list,
            key=lambda row: float(row[self.flammability_index]),
            reverse=True
        )

    def filter_by_flammability(self, threshold):
        # Flammability 값이 threshold 이상인 행들만 반환
        return [row for row in self.data_list if float(row[self.flammability_index]) >= threshold]
