import tkinter as tk
from tkinter import messagebox

from .comparator import highlight_diff
from .excel_handler import *

# 기본 폰트 설정 (맑은 고딕)
default_font = ("맑은 고딕", 14)

# Excel 데이터프레임 전역 변수
df = None


# 글자 수 계산 함수
def calculate_text_length(content):
    """
    주어진 텍스트 내용의 글자 수를 계산하는 함수.
    """
    byte_length = len(content.encode('utf-8'))
    char_length = len(content)
    result = (byte_length - char_length) * 2 + char_length
    return result


# 텍스트 변경 시 글자 수 갱신 함수
def update_label_count(text_widget, label_count):
    """
    텍스트 위젯의 내용을 기반으로 글자 수를 계산하고 라벨에 업데이트하는 함수.
    """
    content = text_widget.get("1.0", "end-1c")  # 텍스트 내용 가져오기 (마지막 개행 제외)
    length = calculate_text_length(content)  # 글자 수 계산
    label_count.config(text=f"글자 바이트 수: {length}")  # 라벨 업데이트


def open_file(parent):
    global df

    try:
        df = load_excel_file(listbox)  # 엑셀 파일 로드 및 리스트박스 업데이트
    except ValueError as e:
        messagebox.showerror("오류", str(e))
    finally:
        parent.focus_force()  # 파일 열기 후 팝업 창에 포커


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
        text_box1.config(state="normal")  # 읽기 전용 해제 (데이터 삽입을 위해)
        text_box1.delete("1.0", tk.END)
        text_box1.insert(tk.END, text1)
        text_box1.config(state="disabled")  # 다시 읽기 전용으로 설정

        text_box2.delete("1.0", tk.END)
        text_box2.insert(tk.END, text2)

        update_edittext_logic()
    except Exception as e:
        messagebox.showerror("오류", str(e))


# 래퍼 함수: 이벤트 핸들러에서 매개변수를 전달하기 위한 함수
def on_text_change(event):
    update_edittext_logic()


def update_edittext_logic():
    highlight_diff(text_box1, text_box2)

    update_label_count(text_box1, label_count_1)
    update_label_count(text_box2, label_count_2)


def copy_to_clipboard(text_widget):
    """
    주어진 텍스트 위젯의 내용을 클립보드에 복사하는 함수.
    """
    content = text_widget.get("1.0", "end-1c")  # 텍스트 내용 가져오기 (마지막 개행 제외)
    text_widget.clipboard_clear()  # 클립보드 초기화
    text_widget.clipboard_append(content)  # 클립보드에 텍스트 추가


def text_differ(parent):
    global listbox, text_box1, text_box2, label_count_1, label_count_2, df  # 전역 변수 선언

    # 새로운 창 생성
    diff_window = tk.Toplevel(parent)  # 부모 창을 기반으로 새로운 창 생성
    diff_window.title("텍스트 비교")

    # 초기 크기 설정 (살짝 줄임)
    diff_window.geometry("900x600")  # 초기 창 크기 (너비 x 높이)
    diff_window.minsize(700, 500)    # 최소 크기 설정 (너비 x 높이)

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

    # 텍스트 박스와 글자 수 표시 영역 추가
    frame_text_1 = tk.Frame(frame_right)  # 첫 번째 텍스트 박스와 글자 수 영역
    frame_text_1.grid(row=0, column=0, sticky="nsew")

    frame_text_2 = tk.Frame(frame_right)  # 두 번째 텍스트 박스와 글자 수 영역
    frame_text_2.grid(row=0, column=1, sticky="nsew")

    # 첫 번째 텍스트 박스 위에 글자 수 표시
    label_count_1 = tk.Label(frame_text_1, text="글자 바이트 수: 0", font=default_font)
    label_count_1.grid(row=0, column=0, sticky="nsew", pady=(5, 0))

    text_box1 = tk.Text(frame_text_1, height=20, width=50, font=default_font, state="disabled")
    text_box1.grid(row=1, column=0, sticky="nsew")

    button_1 = tk.Button(frame_text_1, text="왼쪽 복사", font=default_font,
                         command=lambda: copy_to_clipboard(text_box1))  # 왼쪽 버튼 추가
    button_1.grid(row=2, column=0, sticky="nsew", pady=(5, 10))

    # 두 번째 텍스트 박스 위에 글자 수 표시
    label_count_2 = tk.Label(frame_text_2, text="글자 바이트 수: 0", font=default_font)
    label_count_2.grid(row=0, column=0, sticky="nsew", pady=(5, 0))

    text_box2 = tk.Text(frame_text_2, height=20, width=50, font=default_font)
    text_box2.grid(row=1, column=0, sticky="nsew")

    button_2 = tk.Button(frame_text_2, text="오른쪽 복사", font=default_font,
                         command=lambda: copy_to_clipboard(text_box2))  # 오른쪽 버튼 추가
    button_2.grid(row=2, column=0, sticky="nsew", pady=(5, 10))

    # 이벤트 바인딩 (래퍼 함수를 사용하여 매개변수 전달)
    text_box1.bind("<KeyRelease>", on_text_change)
    text_box2.bind("<KeyRelease>", on_text_change)

    # 메뉴바 추가 (파일 열기 기능 포함)
    menu_bar = tk.Menu(diff_window)  # 기본 Menu 위젯 생성
    file_menu = tk.Menu(menu_bar, tearoff=0)  # 서브 메뉴 생성

    file_menu.add_command(label="파일 열기", command=lambda: open_file(diff_window))
    menu_bar.add_cascade(label="파일", menu=file_menu)

    diff_window.config(menu=menu_bar)

    # 오른쪽 영역의 비율 설정 (글자 바이트 수:텍스트 박스:버튼 = 1:8:1)
    for frame in [frame_text_1, frame_text_2]:
        frame.rowconfigure(0, weight=1)  # 글자 바이트 수 라벨
        frame.rowconfigure(1, weight=8)  # 텍스트 박스
        frame.rowconfigure(2, weight=1)  # 버튼
        frame.columnconfigure(0, weight=1)

    # frame_right 내부 열 비율 동일하게 설정
    frame_right.grid_columnconfigure(0, weight=1)  # 첫 번째 텍스트 프레임
    frame_right.grid_columnconfigure(1, weight=1)  # 두 번째 텍스트 프레임

    # diff_window 전체 창 비율 확인 및 조정
    diff_window.grid_rowconfigure(0, weight=1)
    diff_window.grid_columnconfigure(0, weight=1)  # 리스트박스 영역 (frame_left)
    diff_window.grid_columnconfigure(1, weight=3)  # 텍스트 비교 영역 (frame_right)

    frame_left.grid_rowconfigure(0, weight=1)  # 리스트박스가 동적으로 확장되도록 설정
    frame_left.grid_columnconfigure(0, weight=1)

    frame_right.grid_rowconfigure(0, weight=1)  # 텍스트 박스가 동적으로 확장되도록 설정
    frame_right.grid_columnconfigure(0, weight=1)  # 왼쪽 텍스트 박스 확장
