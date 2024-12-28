from tkinter import Toplevel, Label

def text_verifier(parent, file_path):
    window_a = Toplevel(parent)
    window_a.title("A Window")
    window_a.geometry("200x150")

    label = Label(window_a, text="A 창 내용", font=("Arial", 12))
    label.pack(pady=20)
