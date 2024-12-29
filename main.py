import tkinter as tk
import webbrowser
from tkinter import Frame, Label, Button, StringVar, messagebox

from tkinterdnd2 import TkinterDnD, DND_FILES

from configs.hash import sha_256_hash
from text_differ.gui_text_differ import TextDiffer
from text_verifier.gui_text_verifier import TextVerifier

# 기본 폰트 설정
default_font = ("맑은 고딕", 25)
xlsx_file_path = ""

# 제작자 및 버전 정보
AUTHOR = "운양고등학교 이종환T"
VERSION = "2024.12.29"


def create_main_window():
    """
    메인 창을 생성하고 GUI 요소를 배치하는 함수.
    """
    root = TkinterDnD.Tk()  # Tk 대신 TkinterDnD.Tk 사용
    root.title("GPTextVerifier")
    root.geometry("800x600")

    # 파일 경로 저장을 위한 StringVar
    file_path_var = StringVar()
    file_path_var.set("이곳에 파일을 Drag & Drop 해주세요.")

    configure_root_layout(root)
    create_top_frame(root, file_path_var)
    create_bottom_frame(root, file_path_var)

    # 메뉴바 생성
    menubar = tk.Menu(root)
    about_menu = tk.Menu(menubar, tearoff=0)
    about_menu.add_command(label="프로그램 정보", command=on_info_click)
    about_menu.add_command(label="GitHub 바로가기", command=on_github_click)
    about_menu.add_command(label="Hash 생성", command=lambda: on_hash_click(root))
    menubar.add_cascade(label="About", menu=about_menu)
    root.config(menu=menubar)

    root.mainloop()


def configure_root_layout(root):
    """
    루트 창의 전체 레이아웃 비율을 설정하는 함수.
    """
    root.grid_rowconfigure(0, weight=1)  # 상단 영역
    root.grid_rowconfigure(1, weight=1)  # 하단 영역
    root.grid_columnconfigure(0, weight=1)  # 전체 창 너비를 균등하게 사용


def create_top_frame(root, file_path_var):
    """
    상단 프레임을 생성하고 파일 경로를 표시하는 함수.
    """
    frame_top = Frame(root, bg="lightgray")
    frame_top.grid(row=0, column=0, sticky="nsew")

    label = Label(frame_top, textvariable=file_path_var, font=default_font, bg="lightgray")
    label.pack(expand=True)

    # 드래그 앤 드롭 이벤트 처리
    def on_file_drop(event):
        """
        드래그 앤 드롭 이벤트 처리.
        """
        # event.data에서 파일 경로를 가져오고 공백 처리를 포함해 정리
        file_path = event.data.strip()

        # Windows 경로의 경우 중괄호로 감싸져 있을 수 있으므로 제거
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]

        # 파일 경로를 StringVar에 설정
        file_path_var.set(file_path)

        global xlsx_file_path
        xlsx_file_path = file_path

    root.drop_target_register(DND_FILES)  # 드래그 앤 드롭 활성화
    root.dnd_bind('<<Drop>>', on_file_drop)  # 드롭 이벤트 바인딩


def create_bottom_frame(root, file_path_var):
    """
    하단 프레임을 생성하고 버튼을 배치하는 함수.
    """
    frame_bottom = Frame(root)
    frame_bottom.grid(row=1, column=0, sticky="nsew")

    configure_bottom_frame_layout(frame_bottom)

    create_button(
        frame_bottom,
        "텍스트 검증 도구",
        0,
        "lightblue",
        lambda: TextVerifier(root, xlsx_file_path)
    )
    create_button(
        frame_bottom,
        "텍스트 비교 도구",
        1,
        "lightgreen",
        lambda: TextDiffer(root, xlsx_file_path)
    )


def configure_bottom_frame_layout(frame):
    """
    하단 프레임의 레이아웃 비율을 설정하는 함수.
    """
    frame.grid_columnconfigure(0, weight=1)  # 왼쪽 버튼 영역
    frame.grid_columnconfigure(1, weight=1)  # 오른쪽 버튼 영역
    frame.grid_rowconfigure(0, weight=1)  # 버튼의 세로 방향 확장


def create_button(frame, text, column, bg_color, command):
    """
    하단 프레임에 버튼을 생성하고 배치하는 함수.

    :param frame: 버튼이 추가될 프레임
    :param text: 버튼에 표시될 텍스트
    :param column: 버튼의 열 위치
    :param bg_color: 버튼의 배경색
    :param command: 버튼 클릭 시 실행될 함수
    """
    button = Button(
        frame,
        text=text,
        font=default_font,
        bg=bg_color,
        fg="black",
        command=command
    )
    button.grid(row=0, column=column, sticky="nsew", padx=10, pady=10)


def on_info_click():
    info_title = "프로그램 정보"
    info_message = (
        f"제작자: {AUTHOR}\n"
        f"버전: {VERSION}\n"
        "\n"
        "GPTextVerifier는 OpenAI의 ChatGPT와 연동하여 한국어 맞춤법 및 문맥을 일괄 교정하는 프로그램입니다.\n"
        "\n"
        "이 프로그램은 LGPL-2.1 라이선스 하에 배포되며, 자유롭게 사용 및 수정할 수 있습니다."
    )

    messagebox.showinfo(info_title, info_message)


def on_github_click():
    webbrowser.open("https://github.com/itmir913/GPTextVerifier/releases")


def on_hash_click(parent):
    sha_256 = sha_256_hash()

    hash_title = "프로그램 정보"
    hash_message = (
        f"SHA-256 Hash: {sha_256}"
    )

    parent.clipboard_clear()  # 기존 클립보드 내용 삭제
    parent.clipboard_append(sha_256)  # 새로운 텍스트 추가

    messagebox.showinfo(hash_title, hash_message)


if __name__ == "__main__":
    create_main_window()
