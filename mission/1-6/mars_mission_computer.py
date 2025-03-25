import random

LOG_FILE_PATH = 'dummy_sensor.log'

class DummySensor:
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0,
            'mars_base_external_temperature': 0,
            'mars_base_internal_humidity': 0,
            'mars_base_external_illuminance': 0,
            'mars_base_internal_co2': 0,
            'mars_base_internal_oxygen': 0
        }
    
    def set_env(self):
        self.env_values['mars_base_internal_temperature'] = random.randint(18, 30)       # 18~30도
        self.env_values['mars_base_external_temperature'] = random.randint(0, 21)        # 0~21도
        self.env_values['mars_base_internal_humidity'] = random.randint(50, 60)          # 50~60%
        self.env_values['mars_base_external_illuminance'] = random.randint(500, 715)     # 500~715 W/m2
        self.env_values['mars_base_internal_co2'] = round(random.uniform(0.02, 0.1), 2)  # 0.02~0.1%
        self.env_values['mars_base_internal_oxygen'] = random.randint(4, 7)              # 4~7%

    def get_env(self):
        self.log_sensor_data()
        return self.env_values

    def log_sensor_data(self):
        current_time = RandomTimeGenerator().get_random_time() # 난수로 현재 시간 생성
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
            for key, value in self.env_values.items():
                f.write(f'[{current_time}] {key}: {value}\n')

class RandomTimeGenerator:
    def get_random_time(self):
        year = 2025
        month = random.randint(1, 12)
        if month in (1, 3, 5, 7, 8, 10, 12):
            day_max = 31
        elif month == 2:
            day_max = 28
        else:
            day_max = 30

        day = random.randint(1, day_max)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)

        time_str = f'{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}'
        return time_str

if __name__ == '__main__':
    ds = DummySensor()
    ds.set_env()                 # 난수 생성으로 sensor 값 초기화
    sensor_values = ds.get_env() # sensor 값 가져오기
    print(sensor_values)
