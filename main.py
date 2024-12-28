from tkinter import Tk, Frame, Label, Button

from text_differ.gui_text_differ import text_differ
from text_verifier.gui_text_verifier import text_verifier

# 기본 폰트 설정
default_font = ("맑은 고딕", 25)


def create_main_window():
    """
    메인 창을 생성하고 GUI 요소를 배치하는 함수.
    """
    root = Tk()
    root.title("GPTextVerifier")
    root.geometry("800x600")

    configure_root_layout(root)
    create_top_frame(root)
    create_bottom_frame(root)

    root.mainloop()


def configure_root_layout(root):
    """
    루트 창의 전체 레이아웃 비율을 설정하는 함수.
    """
    root.grid_rowconfigure(0, weight=1)  # 상단 영역
    root.grid_rowconfigure(1, weight=1)  # 하단 영역
    root.grid_columnconfigure(0, weight=1)  # 전체 창 너비를 균등하게 사용


def create_top_frame(root):
    """
    상단 프레임을 생성하고 안내 텍스트를 배치하는 함수.
    """
    frame_top = Frame(root, bg="lightgray")
    frame_top.grid(row=0, column=0, sticky="nsew")

    label = Label(frame_top, text="파일을 선택하세요.", font=default_font, bg="lightgray")
    label.pack(expand=True)


def create_bottom_frame(root):
    """
    하단 프레임을 생성하고 버튼을 배치하는 함수.
    """
    frame_bottom = Frame(root)
    frame_bottom.grid(row=1, column=0, sticky="nsew")

    configure_bottom_frame_layout(frame_bottom)

    create_button(frame_bottom, "텍스트 검증 도구", 0, "lightblue", lambda: text_verifier(root))
    create_button(frame_bottom, "텍스트 비교 도구", 1, "lightgreen", lambda: text_differ(root))


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


if __name__ == "__main__":
    create_main_window()
