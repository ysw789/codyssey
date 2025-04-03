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

    def get_sensor_data(self):
        ds = DummySensor()
        try:
            while True:
                ds.set_env()
                self.env_values = ds.get_env()
                print(self.env_values)
                time.sleep(5)
        except KeyboardInterrupt:
            print('System stopped....')

if __name__ == '__main__':
    RunComputer = MissionComputer()
    RunComputer.get_sensor_data()