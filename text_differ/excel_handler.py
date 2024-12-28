from tkinter import filedialog

import pandas as pd

from configs.config import COLUMN_NAME, COLUMN_BEFORE, COLUMN_AFTER, COLUMN_CLASS, COLUMN_NUMBER  # 변수 가져오기


def load_excel_file(listbox, file_path):
    """
    Excel 파일을 열고 데이터를 읽어 리스트박스에 추가합니다.
    """
    if not file_path:
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if not file_path:
        return None

    # Pandas를 사용하여 Excel 파일 전체 읽기
    df = pd.read_excel(file_path)  # 전체 열 읽기
    listbox.delete(0, "end")

    # 필수 열이 존재하는지 확인
    if COLUMN_NAME not in df.columns or COLUMN_BEFORE not in df.columns or COLUMN_AFTER not in df.columns:
        raise ValueError(f"'{COLUMN_NAME}', '{COLUMN_BEFORE}', '{COLUMN_AFTER}' 열이 누락되었습니다.")

    PLAG_CLASS_AND_NUMBER = False
    # 반과 번호 열이 존재하는지 확인
    if COLUMN_CLASS in df.columns and COLUMN_NUMBER in df.columns:
        PLAG_CLASS_AND_NUMBER = True

    # 리스트박스에 데이터 추가
    for _, row in df.iterrows():
        if PLAG_CLASS_AND_NUMBER:
            # CLASS와 NUMBER 열이 존재하면 "{반}반 {번호}번 {이름}" 형식으로 추가
            formatted_item = f"{row[COLUMN_CLASS]}반 {row[COLUMN_NUMBER]}번 {row[COLUMN_NAME]}"
            listbox.insert("end", formatted_item)
        else:
            # 그렇지 않으면 이름만 추가
            listbox.insert("end", row[COLUMN_NAME])

    return df
