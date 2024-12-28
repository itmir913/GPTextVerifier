from tkinter import *

from text_differ.gui_text_differ import text_differ
from text_verifier.gui_text_verifier import text_verifier

# 기본 폰트 설정
defaultFont = ("맑은 고딕", 25)


def main():
    root = Tk()
    root.title("GPTextVerifier")
    root.geometry("800x600")  # 창 크기 설정

    # 전체 레이아웃을 2개의 영역으로 나눔 (상단과 하단)
    root.grid_rowconfigure(0, weight=1)  # 상단 영역
    root.grid_rowconfigure(1, weight=1)  # 하단 영역
    root.grid_columnconfigure(0, weight=1)  # 전체 창 너비를 균등하게 사용

    # 상단 영역: 파일 선택 안내 텍스트
    frame_top = Frame(root, bg="lightgray")  # 배경색 설정
    frame_top.grid(row=0, column=0, sticky="nsew")

    label = Label(frame_top, text="파일을 선택하세요.", font=defaultFont, bg="lightgray")
    label.pack(expand=True)

    # 하단 영역: 좌우 버튼 배치
    frame_bottom = Frame(root)
    frame_bottom.grid(row=1, column=0, sticky="nsew")

    # 하단 영역의 열 비율 설정
    frame_bottom.grid_columnconfigure(0, weight=1)  # 왼쪽 버튼 영역
    frame_bottom.grid_columnconfigure(1, weight=1)  # 오른쪽 버튼 영역
    frame_bottom.grid_rowconfigure(0, weight=1)  # 버튼의 세로 방향 확장

    # 왼쪽 버튼: text_verifier.text_verifier_gui 열기
    button_a = Button(
        frame_bottom,
        text="텍스트 검증 도구",
        font=defaultFont,
        command=lambda: text_verifier(root),
        bg="lightblue",
        fg="black",
    )
    button_a.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    # 오른쪽 버튼: text_differ.text_differ_gui 열기
    button_b = Button(
        frame_bottom,
        text="텍스트 비교 도구",
        font=defaultFont,
        command=lambda: text_differ(root),
        bg="lightgreen",
        fg="black",
    )
    button_b.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
