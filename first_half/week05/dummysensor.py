import random

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
        return self.env_values