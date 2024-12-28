import tkinter as tk
from tkinter import messagebox

from .config import *
from .excel_handler import *
from .text_comparator import *

# 기본 폰트 설정 (맑은 고딕)
default_font = ("맑은 고딕", 14)

# Excel 데이터프레임 전역 변수
df = None


# 리스트뷰에서 선택한 항목 처리 함수
def on_select(event):
    global df

    selected_index = listbox.curselection()
    if not selected_index or df is None:
        return

    index = selected_index[0]

    try:
        text1 = str(df.iloc[index][COLUMN_BEFORE])  # "수정전" 데이터 가져오기
        text2 = str(df.iloc[index][COLUMN_AFTER])  # "수정후" 데이터 가져오기

        # 텍스트 박스 초기화 및 데이터 삽입
        text_box1.delete("1.0", tk.END)
        text_box2.delete("1.0", tk.END)
        text_box1.insert(tk.END, text1)
        text_box2.insert(tk.END, text2)

        highlight_diff(text_box1, text_box2)  # 직접 호출 시에는 두 텍스트 박스를 전달
    except Exception as e:
        messagebox.showerror("오류", str(e))


# 래퍼 함수: 이벤트 핸들러에서 매개변수를 전달하기 위한 함수
def on_text_change(event):
    highlight_diff(text_box1, text_box2)


def text_differ_gui(parent):
    global listbox, text_box1, text_box2, df  # 전역 변수 선언

    # 새로운 창 생성
    diff_window = tk.Toplevel(parent)  # 부모 창을 기반으로 새로운 창 생성
    diff_window.title("텍스트 비교")

    # 레이아웃 구성 (리스트뷰와 텍스트 박스)
    frame_left = tk.Frame(diff_window)
    frame_left.grid(row=0, column=0, sticky="nswe")
    frame_right = tk.Frame(diff_window)
    frame_right.grid(row=0, column=1, sticky="nswe")

    # 리스트박스 ("이름" 열 데이터 표시)
    listbox = tk.Listbox(frame_left, width=30, height=20, font=default_font)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    listbox.bind("<<ListboxSelect>>", on_select)

    scrollbar = tk.Scrollbar(frame_left)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    # 텍스트 박스 ("수정전"과 "수정후" 데이터 비교용)
    text_box1 = tk.Text(frame_right, height=20, width=50, font=default_font)
    text_box1.grid(row=0, column=0, sticky="nsew")
    text_box1.tag_configure("highlight", background="lightcoral")

    text_box2 = tk.Text(frame_right, height=20, width=50, font=default_font)
    text_box2.grid(row=0, column=1, sticky="nsew")
    text_box2.tag_configure("highlight", background="lightgreen")

    # 이벤트 바인딩 (래퍼 함수를 사용하여 매개변수 전달)
    text_box1.bind("<KeyRelease>", on_text_change)
    text_box2.bind("<KeyRelease>", on_text_change)

    # 메뉴바 추가 (파일 열기 기능 포함)
    menu_bar = tk.Menu(diff_window)  # 기본 Menu 위젯 생성
    file_menu = tk.Menu(menu_bar, tearoff=0)  # 서브 메뉴 생성

    file_menu.add_command(label="파일 열기", command=open_file)
    menu_bar.add_cascade(label="파일", menu=file_menu)

    diff_window.config(menu=menu_bar)

    # Grid 레이아웃의 행과 열에 weight 설정 (동적 크기 조정을 위해 필수)
    diff_window.grid_rowconfigure(0, weight=1)
    diff_window.grid_columnconfigure(0, weight=1)  # 첫 번째 열 (frame_left)이 확장되도록 설정
    diff_window.grid_columnconfigure(1, weight=3)  # 두 번째 열 (frame_right)이 더 많이 확장되도록 설정

    frame_left.grid_rowconfigure(0, weight=1)  # 리스트박스가 동적으로 확장되도록 설정
    frame_left.grid_columnconfigure(0, weight=1)

    frame_right.grid_rowconfigure(0, weight=1)  # 텍스트 박스가 동적으로 확장되도록 설정
    frame_right.grid_columnconfigure(0, weight=1)  # 왼쪽 텍스트 박스 확장
    frame_right.grid_columnconfigure(1, weight=1)  # 오른쪽 텍스트 박스 확장


def open_file():
    global df

    try:
        df = load_excel_file(listbox)  # 엑셀 파일 로드 및 리스트박스 업데이트
    except ValueError as e:
        messagebox.showerror("오류", str(e))
