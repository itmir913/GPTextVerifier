import tkinter as tk
from tkinter import messagebox, filedialog

from configs.config import *
from configs.excel_handler import load_excel_file
from .comparator import highlight_diff

# 기본 폰트 설정
default_font = ("맑은 고딕", 14)


def calculate_text_length(content):
    """텍스트 내용의 글자 수를 계산."""
    byte_length = len(content.encode('utf-8'))
    char_length = len(content)
    return (byte_length - char_length) * 2 + char_length


def update_label_count(text_widget, label):
    """텍스트 위젯의 글자 수를 라벨에 갱신."""
    content = text_widget.get("1.0", "end-1c")
    label.config(text=f"글자 바이트 수: {calculate_text_length(content)}")


def copy_to_clipboard_with_feedback(button, text_widget):
    """
    텍스트 위젯의 내용을 클립보드에 복사하고 버튼 텍스트를 일시적으로 변경.
    """
    content = text_widget.get("1.0", "end-1c")  # 텍스트 내용 가져오기
    text_widget.clipboard_clear()  # 클립보드 초기화
    text_widget.clipboard_append(content)  # 클립보드에 텍스트 추가

    # 버튼 텍스트를 "복사됨"으로 변경
    original_text = button.cget("text")
    button.config(text="복사됨")

    # 2초 후 버튼 텍스트를 원래 상태로 복원
    button.after(2000, lambda: button.config(text=original_text))


def update_edittext_logic(text_box1, text_box2, label1, label2):
    """텍스트 상자 내용 비교 및 업데이트."""
    highlight_diff(text_box1, text_box2)
    update_label_count(text_box1, label1)
    update_label_count(text_box2, label2)


def open_file(parent, listbox, file_path):
    """엑셀 파일을 열고 리스트박스 갱신."""
    global df
    try:
        if not file_path:
            file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])

        df = load_excel_file(file_path)
        listbox.delete(0, "end")

        # 필수 열이 존재하는지 확인
        if COLUMN_NAME not in df.columns or COLUMN_BEFORE not in df.columns or COLUMN_AFTER not in df.columns:
            raise ValueError(f"'{COLUMN_NAME}', '{COLUMN_BEFORE}', '{COLUMN_AFTER}' 열이 누락되었습니다.")

        PLAG_CLASS_AND_NUMBER = False
        # 반과 번호 열이 존재하는지 확인
        if COLUMN_CLASS in df.columns and COLUMN_NUMBER in df.columns:
            PLAG_CLASS_AND_NUMBER = True

        PLAG_STATUS = False
        if COLUMN_STATUS in df.columns:
            PLAG_STATUS = True

        # 리스트박스에 데이터 추가
        for index, row in df.iterrows():
            if PLAG_CLASS_AND_NUMBER:
                # CLASS와 NUMBER 열이 존재하면 "{반}반 {번호}번 {이름}" 형식으로 추가
                formatted_item = f"{row[COLUMN_CLASS]}반 {row[COLUMN_NUMBER]}번 {row[COLUMN_NAME]}"
                listbox.insert("end", formatted_item)
            else:
                # 그렇지 않으면 이름만 추가
                listbox.insert("end", row[COLUMN_NAME])

            if PLAG_STATUS:
                if row[COLUMN_STATUS] == PLAG_STATUS_SUCCESS:
                    listbox.itemconfig(index, {'bg': 'green', 'fg': 'white'})
                elif row[COLUMN_STATUS] == PLAG_STATUS_FAIL:
                    listbox.itemconfig(index, {'bg': 'red', 'fg': 'white'})


    except ValueError as e:
        messagebox.showerror("오류", str(e))
    except Exception as e:
        messagebox.showerror("오류", str(e))
    finally:
        parent.focus_force()


def on_select(event, listbox, text_box1, text_box2, label1, label2):
    """리스트박스 선택 항목 처리."""
    global df

    selected_index = listbox.curselection()
    if not selected_index or df is None:
        return

    index = selected_index[0]
    try:
        text1 = str(df.iloc[index][COLUMN_BEFORE])
        text2 = str(df.iloc[index][COLUMN_AFTER])

        text_box1.config(state="normal")
        text_box1.delete("1.0", tk.END)
        text_box1.insert(tk.END, text1)
        text_box1.config(state="disabled")

        text_box2.delete("1.0", tk.END)
        text_box2.insert(tk.END, text2)

        update_edittext_logic(text_box1, text_box2, label1, label2)
    except Exception as e:
        messagebox.showerror("오류", str(e))


def create_text_frame(parent, label_text, copy_command):
    """
    텍스트 상자와 관련 요소 생성.
    """
    frame = tk.Frame(parent)

    label = tk.Label(frame, text=label_text, font=default_font)
    label.grid(row=0, column=0, sticky="nsew", pady=(5, 0))

    text_box = tk.Text(frame, height=20, width=50, font=default_font)
    text_box.grid(row=1, column=0, sticky="nsew")

    button = tk.Button(
        frame,
        text="복사",
        font=default_font,
        command=lambda: copy_command(button, text_box)
    )
    button.grid(row=2, column=0, sticky="nsew", pady=(5, 10))

    frame.rowconfigure(0, weight=1)
    frame.rowconfigure(1, weight=8)
    frame.rowconfigure(2, weight=1)
    frame.columnconfigure(0, weight=1)

    return frame, text_box, label


def text_differ(parent, file_path):
    """텍스트 비교 도구 창 생성."""
    global df

    diff_window = tk.Toplevel(parent)
    diff_window.title("텍스트 비교")
    diff_window.geometry("900x600")
    diff_window.minsize(700, 500)

    frame_left = tk.Frame(diff_window)
    frame_left.grid(row=0, column=0, sticky="nswe")

    frame_right = tk.Frame(diff_window)
    frame_right.grid(row=0, column=1, sticky="nswe")

    listbox = tk.Listbox(frame_left, width=30, font=default_font)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(frame_left, command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)

    frame_text1, text_box1, label_count1 = create_text_frame(
        frame_right, "글자 바이트 수: 0", copy_to_clipboard_with_feedback
    )
    frame_text1.grid(row=0, column=0, sticky="nsew")

    frame_text2, text_box2, label_count2 = create_text_frame(
        frame_right, "글자 바이트 수: 0", copy_to_clipboard_with_feedback
    )
    frame_text2.grid(row=0, column=1, sticky="nsew")

    listbox.bind(
        "<<ListboxSelect>>",
        lambda e: on_select(e, listbox, text_box1, text_box2, label_count1, label_count2),
    )
    text_box1.bind("<KeyRelease>", lambda e: update_edittext_logic(text_box1, text_box2, label_count1, label_count2))
    text_box2.bind("<KeyRelease>", lambda e: update_edittext_logic(text_box1, text_box2, label_count1, label_count2))

    menu_bar = tk.Menu(diff_window)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="파일 열기", command=lambda: open_file(diff_window, listbox, None))
    menu_bar.add_cascade(label="파일", menu=file_menu)
    diff_window.config(menu=menu_bar)

    frame_left.grid_rowconfigure(0, weight=1)
    frame_left.grid_columnconfigure(0, weight=1)

    frame_right.grid_rowconfigure(0, weight=1)
    frame_right.grid_columnconfigure(0, weight=1)
    frame_right.grid_columnconfigure(1, weight=1)

    diff_window.grid_rowconfigure(0, weight=1)
    diff_window.grid_columnconfigure(0, weight=1)
    diff_window.grid_columnconfigure(1, weight=3)

    if file_path:
        open_file(diff_window, listbox, file_path)
