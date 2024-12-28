import hashlib
import os
import sys


def sha_256_hash():
    # PyInstaller로 패키징한 후 실행되는 경우 sys._MEIPASS가 설정됨
    if getattr(sys, 'frozen', False):
        script_path = os.path.join(sys._MEIPASS, 'main.py')  # 실제 스크립트 이름
    else:
        script_path = __file__

    # 파일을 열어서 내용을 읽어들임
    with open(script_path, 'rb') as file:
        file_content = file.read()

    # SHA-256 해시 계산
    sha256_hash = hashlib.sha256(file_content).hexdigest()
    print(sha256_hash)

    return sha256_hash
