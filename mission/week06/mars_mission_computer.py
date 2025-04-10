import platform
import psutil

SETTINGS_FILE_NAME = 'setting.txt'
NOT_AVAILABLE = 'N/A'
SYS_OS = 'os'
SYS_OS_VERSION = 'os_version'
SYS_CPU_TYPE = 'cpu_type'
SYS_CPU_CORES = 'cpu_cores'
SYS_MEM_SIZE = 'mem_size'
ERR_MSG_COMPUTER_INFO = 'Error: failed to load computer info.'
ERR_MSG_COMPUTER_LOAD = 'Error: failed to load computer load info.'

class MissionComputer:
    def read_settings(self):
        try:
            with open(SETTINGS_FILE_NAME, 'r', encoding='utf-8') as f:
                keys = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                return keys
        except FileNotFoundError:
            # 파일이 없으면 전체 항목 반환
            return [SYS_OS, SYS_OS_VERSION, SYS_CPU_TYPE, SYS_CPU_CORES, SYS_MEM_SIZE]

    def get_mission_computer_info(self):
        setting_keys = self.read_settings()
        try:
            data = {
                SYS_OS: platform.system(),
                SYS_OS_VERSION: platform.version(),
                SYS_CPU_TYPE: platform.processor(),
                SYS_CPU_CORES: psutil.cpu_count() if psutil else NOT_AVAILABLE,
                SYS_MEM_SIZE: f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB" if psutil else NOT_AVAILABLE
            }

            # 설정 파일에 정의된 키만 필터링
            filtered_info = { key: data[key] for key in setting_keys if key in data }
            
            print(str(filtered_info).replace("'", '"'))
        except Exception as e:
            print(ERR_MSG_COMPUTER_INFO)

    def get_mission_computer_load(self):
        try:
            cpu_usage = psutil.cpu_percent(interval=1) if psutil else NOT_AVAILABLE
            mem_usage = psutil.virtual_memory().percent if psutil else NOT_AVAILABLE

            # 정수나 실수라면 % 기호 추가
            if isinstance(cpu_usage, (int, float)):
                cpu_usage = f'{cpu_usage}%'
            if isinstance(mem_usage, (int, float)):
                mem_usage = f'{mem_usage}%'

            load_info = {
                'cpu_usage': cpu_usage,
                'mem_usage': mem_usage
            }

            print(str(load_info).replace("'", '"'))
        except Exception as e:
            print(ERR_MSG_COMPUTER_LOAD)

if __name__ == '__main__':
    runComputer = MissionComputer()
    runComputer.get_mission_computer_info()
    runComputer.get_mission_computer_load()
