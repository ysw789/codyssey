from dummysensor import DummySensor

import time

class MissionComputer:
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0,
            'mars_base_external_temperature': 0,
            'mars_base_internal_humidity': 0,
            'mars_base_external_illuminance': 0,
            'mars_base_internal_co2': 0,
            'mars_base_internal_oxygen': 0
        }
        # 각 key 별 수집된 데이터 저장을 위한 리스트
        self.collected_data = {key: [] for key in self.env_values.keys()}
        # 주기 카운터
        self.counter = 0

    def get_sensor_data(self):
        ds = DummySensor()
        try:
            while True:
                # 센서 데이터 생성 및 출력
                ds.set_env()
                self.env_values = ds.get_env()
                print(self.env_values)

                # 수집한 데이터를 저장
                for key, value in self.env_values.items():
                    self.collected_data[key].append(value)
                
                # 카운터 증가
                self.counter += 1
                
                # 카운터가 60회(5분)에 도달하면 평균 계산 및 출력
                if self.counter >= 60:
                    self.calculate_and_print_averages()

                    # 새로운 5분 주기를 위해 리스트 및 카운터 초기화
                    self.collected_data = {key: [] for key in self.env_values.keys()}
                    self.counter = 0

                # 5초 대기
                time.sleep(5)
        except KeyboardInterrupt: # Ctrl+C로 종료 시
            print('System stopped....')

    def calculate_and_print_averages(self):
        print("\n===== Last 5 minutes avg =====")
        # 각 key 별 평균 계산 및 출력
        for key, values in self.collected_data.items():
            if values:
                avg_value = sum(values) / len(values)
                print(f"{key}: {avg_value:.2f}")
        print("===========================\n")

if __name__ == '__main__':
    RunComputer = MissionComputer()
    RunComputer.get_sensor_data()