from tkinter import *

from text_differ import text_differ
from text_verifier import text_verifier


def main():
    root = Tk()
    root.title("GPTextVerifier")

    label = Label(root, text="메인 화면", font=("Arial", 14))
    label.pack(pady=20)

    button_a = Button(root, text="A 창 열기", command=lambda: text_differ.text_differ_gui(root))
    button_a.pack(pady=10)

    button_b = Button(root, text="B 창 열기", command=lambda: text_verifier.text_verifier_gui(root))
    button_b.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
