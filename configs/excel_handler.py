import pandas as pd


def load_excel_file(file_path):
    """
    Excel 파일을 열고 데이터를 읽어 리스트박스에 추가합니다.
    """
    if not file_path:
        return None

    try:
        # 파일이 다른 프로그램에서 열려 있는지 확인
        with open(file_path, "w") as file:

            # 파일을 Pandas로 읽기
            df = pd.read_excel(file)
            return df

    except FileNotFoundError:
        print("파일이 존재하지 않습니다.")
    except PermissionError:
        print("파일이 다른 프로그램에서 사용 중입니다.")
    except Exception as e:
        print(f"오류 발생: {e}")

    return None
