import configparser

# 열 이름을 변수로 관리
COLUMN_NAME = "이름"  # NAME 값이 담긴 열 이름
COLUMN_BEFORE = "수정전"  # 기존 값이 담긴 열 이름
COLUMN_AFTER = "수정후"  # 수정된 값이 담긴 열 이름
COLUMN_CLASS = "반"  # CLASS 값이 담긴 열 이름
COLUMN_NUMBER = "번호"  # NUMBER 값이 담긴 열 이름

COLUMN_STATUS = "상태"
PLAG_STATUS_SUCCESS = "Success"
PLAG_STATUS_FAIL = "Fail"


class ConfigSingleton:
    """싱글톤 패턴으로 ConfigParser 관리"""
    _instance = None

    def __new__(cls, file_path='config.txt'):
        if cls._instance is None:
            cls._instance = super(ConfigSingleton, cls).__new__(cls)
            cls._instance._config = configparser.ConfigParser()
            cls._instance._config.read(file_path)
        return cls._instance

    @property
    def config(self):
        return self._config
