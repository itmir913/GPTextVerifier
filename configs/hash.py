import hashlib
import os
import sys

# 캐시를 위한 딕셔너리 생성
hash_cache = {}


def sha_256_hash():
    # PyInstaller로 패키징된 경우 실행 파일 경로를 가져옴
    if getattr(sys, 'frozen', False):
        script_path = sys.executable  # 현재 실행 중인 바이너리 파일 경로
    else:
        script_path = __file__

    # 캐시에 해시가 이미 저장되어 있는지 확인
    if script_path in hash_cache:
        return hash_cache[script_path]

    # 바이너리 파일을 열어서 내용을 읽어들임
    with open(script_path, 'rb') as file:
        file_content = file.read()

    # SHA-256 해시 계산
    sha256_hash = hashlib.sha256(file_content).hexdigest()

    # 해시를 캐시에 저장
    hash_cache[script_path] = sha256_hash

    return sha256_hash


if __name__ == "__main__":
    print("Program SHA-256 Hash:", sha_256_hash())
