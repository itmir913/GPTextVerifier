import tkinter as tk
from tkinter import messagebox, filedialog
from configs.config import *
from configs.excel_handler import load_excel_file
from .comparator import highlight_diff


class TextDiffer:
    def __init__(self, parent, file_path=None):
        self.parent = parent
        self.file_path = file_path
        self.df = None
        self.default_font = ("맑은 고딕", 14)
        self.setup_ui()
        if self.file_path:
            self.open_file()

    def setup_ui(self):
        self.diff_window = tk.Toplevel(self.parent)
        self.diff_window.title("텍스트 비교")
        self.diff_window.geometry("900x600")
        self.diff_window.minsize(700, 500)

        self.frame_left = tk.Frame(self.diff_window)
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        self.frame_right = tk.Frame(self.diff_window)
        self.frame_right.grid(row=0, column=1, sticky="nswe")

        self.listbox = tk.Listbox(self.frame_left, width=30, font=self.default_font)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(self.frame_left, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        frame_text1, self.text_box1, self.label_count1 = self.create_text_frame(
            self.frame_right, "글자 바이트 수: 0", self.copy_to_clipboard, "수정전 복사"
        )
        frame_text1.grid(row=0, column=0, sticky="nsew")

        frame_text2, self.text_box2, self.label_count2 = self.create_text_frame(
            self.frame_right, "글자 바이트 수: 0", self.save_and_copy_to_clipboard, "수정후 저장 및 복사"
        )
        frame_text2.grid(row=0, column=1, sticky="nsew")

        self.listbox.bind(
            "<<ListboxSelect>>",
            lambda e: self.on_select(e)
        )
        self.text_box1.bind(
            "<KeyRelease>",
            lambda e: self.update_edittext_logic()
        )
        self.text_box2.bind(
            "<KeyRelease>",
            lambda e: self.update_edittext_logic()
        )

        menu_bar = tk.Menu(self.diff_window)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="파일 열기", command=self.open_file)
        menu_bar.add_cascade(label="파일", menu=file_menu)
        self.diff_window.config(menu=menu_bar)

        self.frame_left.grid_rowconfigure(0, weight=1)
        self.frame_left.grid_columnconfigure(0, weight=1)

        self.frame_right.grid_rowconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=1)

        self.diff_window.grid_rowconfigure(0, weight=1)
        self.diff_window.grid_columnconfigure(0, weight=1)
        self.diff_window.grid_columnconfigure(1, weight=3)

    def calculate_text_length(self, content):
        return len(content.encode('utf-8'))

    def update_label_count(self, text_widget, label):
        content = text_widget.get("1.0", "end-1c")
        label.config(text=f"글자 바이트 수: {self.calculate_text_length(content)}")

    def copy_to_clipboard(self, button, text_widget):
        content = text_widget.get("1.0", "end-1c")
        text_widget.clipboard_clear()
        text_widget.clipboard_append(content)
        original_text = button.cget("text")
        button.config(text="복사됨")
        button.after(2000, lambda: button.config(text=original_text))

    def save_and_copy_to_clipboard(self, button, text_widget):
        self.copy_to_clipboard(button, text_widget)

        try:
            if self.df is not None:
                message = text_widget.get("1.0", "end-1c")
                selected_index = self.listbox.curselection()
                if selected_index:
                    idx = selected_index[0]
                    self.df.at[idx, COLUMN_AFTER] = message
                    self.df.to_excel(self.file_path, index=False)
        except Exception as e:
            self.show_error(str(e))

    def update_edittext_logic(self):
        highlight_diff(self.text_box1, self.text_box2)
        self.update_label_count(self.text_box1, self.label_count1)
        self.update_label_count(self.text_box2, self.label_count2)

    def open_file(self):
        try:
            if not self.file_path:
                self.file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])

            self.df = load_excel_file(self.file_path)
            self.listbox.delete(0, "end")

            if COLUMN_NAME not in self.df.columns or COLUMN_BEFORE not in self.df.columns or COLUMN_AFTER not in self.df.columns:
                raise ValueError(f"'{COLUMN_NAME}', '{COLUMN_BEFORE}', '{COLUMN_AFTER}' 열이 누락되었습니다.")

            plag_class_and_number = COLUMN_CLASS in self.df.columns and COLUMN_NUMBER in self.df.columns
            plag_status = COLUMN_STATUS in self.df.columns

            for index, row in self.df.iterrows():
                if plag_class_and_number:
                    formatted_item = f"{row[COLUMN_CLASS]}반 {row[COLUMN_NUMBER]}번 {row[COLUMN_NAME]}"
                else:
                    formatted_item = row[COLUMN_NAME]
                self.listbox.insert("end", formatted_item)

                if plag_status:
                    if row[COLUMN_STATUS] == PLAG_STATUS_SUCCESS:
                        self.listbox.itemconfig(index, {'bg': 'green', 'fg': 'white'})
                    elif row[COLUMN_STATUS] == PLAG_STATUS_FAIL:
                        self.listbox.itemconfig(index, {'bg': 'red', 'fg': 'white'})
        except ValueError as e:
            messagebox.showerror("오류", str(e))
        except Exception as e:
            messagebox.showerror("오류", str(e))
        finally:
            self.parent.focus_force()

    def on_select(self, event):
        selected_index = self.listbox.curselection()
        if not selected_index or self.df is None:
            return

        index = selected_index[0]
        try:
            text1 = str(self.df.iloc[index][COLUMN_BEFORE])
            text2 = str(self.df.iloc[index][COLUMN_AFTER])

            self.text_box1.config(state="normal")
            self.text_box1.delete("1.0", tk.END)
            self.text_box1.insert(tk.END, text1)
            self.text_box1.config(state="disabled")

            self.text_box2.delete("1.0", tk.END)
            self.text_box2.insert(tk.END, text2)

            self.update_edittext_logic()
        except Exception as e:
            messagebox.showerror("오류", str(e))

    def create_text_frame(self, parent, label_text, copy_command, button_text):
        frame = tk.Frame(parent)

        label = tk.Label(frame, text=label_text, font=self.default_font)
        label.grid(row=0, column=0, sticky="nsew", pady=(5, 0))

        text_box = tk.Text(frame, height=20, width=50, font=self.default_font)
        text_box.grid(row=1, column=0, sticky="nsew")

        button = tk.Button(
            frame,
            text=button_text,
            font=self.default_font,
            command=lambda: copy_command(button, text_box)
        )
        button.grid(row=2, column=0, sticky="nsew", pady=(5, 10))

        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=8)
        frame.rowconfigure(2, weight=1)
        frame.columnconfigure(0, weight=1)

        return frame, text_box, label

    def show_error(self, message):
        """오류 메시지를 표시합니다."""
        messagebox.showerror("오류", message)
# Example of how to use the class
# root = tk.Tk()
# app = TextDifferApp(root)
# root.mainloop()
