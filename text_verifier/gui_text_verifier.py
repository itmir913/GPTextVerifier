import asyncio
from queue import Queue, Empty
from threading import Thread, Event
from tkinter import Toplevel, Label, Button, StringVar, Frame, messagebox
from tkinter.ttk import Progressbar

import aiohttp
import pandas as pd

from configs.config import *

# 기본 폰트 설정
default_font = ("맑은 고딕", 25)


class TextVerifier:
    def __init__(self, parent, file_path):
        self.parent = parent
        self.file_path = file_path
        self.stop_event = Event()
        self.update_queue = Queue()
        self.df = None  # 엑셀 데이터를 저장할 변수
        self.create_window()

    def create_window(self):
        """텍스트 검증 창을 생성."""
        if not self.file_path:
            messagebox.showerror("오류", "파일을 Drag & Drop 하여 선택하세요.")
            return

        # 새 창 생성
        self.window_a = Toplevel(self.parent)
        self.window_a.title("텍스트 검증 with GPT")
        self.window_a.geometry("800x600")

        # 각 요소를 위한 프레임
        frame = Frame(self.window_a)
        frame.pack(expand=True, fill='both')

        # 상태 표시 라벨
        self.status_var = StringVar(value="")
        label = Label(frame, textvariable=self.status_var, font=default_font)
        label.pack(pady=20, fill='x', expand=True)

        # 진행률 표시바
        self.progress = Progressbar(frame, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10, fill='x', expand=True)

        # 업데이트 상태 확인 시작
        self.window_a.after(100, self.update_status)

        # 엑셀 파일을 읽어서 COLUMN_BEFORE 확인 및 총 데이터 수를 표시
        self.read_excel_and_update_status()

        # 시작 버튼
        start_frame = Frame(frame)
        start_frame.pack(expand=True, fill='both')

        self.start_button = Button(
            start_frame,
            text="작업 시작",
            font=default_font,
            command=self.start_task
        )
        self.start_button.pack(fill='both', expand=True)

        # 닫기 버튼
        close_frame = Frame(frame)
        close_frame.pack(expand=True, fill='both')

        close_button = Button(close_frame, text="닫기", font=default_font, command=self.close_window)
        close_button.pack(fill='both', expand=True)

    def read_excel_and_update_status(self):
        """엑셀 파일을 읽어 COLUMN_BEFORE 확인 및 총 데이터 표시."""
        try:
            self.df = pd.read_excel(self.file_path)  # 한 번만 읽기

            if COLUMN_BEFORE not in self.df.columns:
                messagebox.showerror("오류", f"엑셀 파일에 {COLUMN_BEFORE} 열이 없습니다.")
                return

            total_rows = len(self.df)
            self.status_var.set(f"총 데이터 개수: {total_rows}")

        except Exception as e:
            messagebox.showerror("오류", f"엑셀 파일 읽기 오류: {str(e)}")
            self.window_a.destroy()  # 창 닫기

    def start_task(self):
        """작업을 시작하고 버튼을 비활성화."""
        self.start_button.config(state='disabled')  # 버튼 비활성화
        self.stop_event.clear()  # 중지 이벤트 초기화
        Thread(target=self.run_in_thread).start()

    def run_in_thread(self):
        """새 쓰레드에서 이벤트 루프 실행."""
        asyncio.run(self.process_text(self.file_path, self.update_queue))

    async def process_text(self, file_path, update_queue):
        """엑셀 파일 처리 및 HTTP POST 요청."""
        try:
            if self.df is None:
                messagebox.showerror("오류", "데이터가 로드되지 않았습니다.")
                return

            self.df[COLUMN_AFTER] = ""  # 요청 결과 저장을 위한 열 추가
            total_rows = len(self.df)

            async with aiohttp.ClientSession() as session:
                for idx, row in self.df.iterrows():
                    if self.stop_event.is_set():  # 중단 요청 확인
                        update_queue.put(("작업이 중단되었습니다.", 0))
                        return

                    data = {"hash": "123", "content": row[COLUMN_BEFORE]}
                    try:
                        response = await self.send_post_request(session, data)
                        self.df.at[idx, COLUMN_AFTER] = response["message"] if response["success"] else "실패"
                    except Exception as e:
                        self.df.at[idx, COLUMN_AFTER] = f"오류: {str(e)}"

                    progress_value = (idx + 1) / total_rows * 100
                    update_queue.put((f"진행 중: {idx + 1}/{total_rows} 처리 완료", progress_value))
                    await asyncio.sleep(0.1)

            output_file = file_path.replace(".xlsx", "_결과.xlsx")
            self.df.to_excel(output_file, index=False)
            update_queue.put((f"작업 완료! 결과가 {output_file}에 저장되었습니다.", total_rows))
        except Exception as e:
            update_queue.put((f"오류 발생: {str(e)}", 0))

    async def send_post_request(self, session, data):
        """HTTP POST 요청을 보내는 함수."""
        url = "http://example.com/api"  # 실제 API URL로 변경
        async with session.post(url, json=data) as response:
            if response.status != 200:
                raise Exception(f"HTTP {response.status}")
            return await response.json()

    def update_status(self):
        """큐에서 메시지를 꺼내 상태 업데이트."""
        try:
            while True:
                message, progress_value = self.update_queue.get_nowait()
                self.status_var.set(message)
                self.progress["value"] = progress_value
                if progress_value >= 100:
                    self.start_button.config(state='normal')  # 버튼 활성화
        except Empty:
            self.window_a.after(100, self.update_status)

    def close_window(self):
        """창을 닫을 때 호출되는 함수."""
        self.stop_event.set()  # 작업 중지 요청
        self.window_a.destroy()