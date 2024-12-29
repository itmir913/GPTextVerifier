import asyncio
import os
from queue import Queue, Empty
from threading import Thread, Event
from tkinter import Toplevel, Label, Button, StringVar, Frame, messagebox
from tkinter.ttk import Progressbar

import aiohttp

from configs.api_url import API_URL
from configs.config import *
from configs.excel_handler import load_excel_file
from configs.hash import sha_256_hash

# 기본 폰트 설정
default_font = ("맑은 고딕", 25)


class TextVerifier:
    def __init__(self, parent, file_path):
        self.parent = parent
        self.file_path = file_path
        self.stop_event = Event()
        self.update_queue = Queue()

        try:
            self.df = load_excel_file(file_path)
        except Exception as e:
            self.show_error(str(e))
            return

        self.create_window()

    def create_window(self):
        """텍스트 검증 창을 생성."""
        if not self.file_path or not os.path.isfile(self.file_path):
            self.show_error("유효한 파일을 선택해주세요.")
            return

        self.window_a = self._initialize_window()
        self._setup_gui_elements()

        self.window_a.after(100, self.update_status)
        self.load_excel_data()

    def _initialize_window(self):
        """새 창을 초기화하고 반환합니다."""
        window = Toplevel(self.parent)
        window.title("텍스트 검증 with GPT")
        window.geometry("800x600")
        window.protocol("WM_DELETE_WINDOW", self.close_window)
        return window

    def _setup_gui_elements(self):
        """GUI 요소를 설정합니다."""
        frame = Frame(self.window_a)
        frame.pack(expand=True, fill='both')

        self.status_var = StringVar(value="")
        label = Label(frame, textvariable=self.status_var, font=default_font)
        label.pack(pady=10, fill='x', expand=True)

        self.progress = Progressbar(frame, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10, fill='x', expand=True)

        self._setup_control_buttons(frame)

    def _setup_control_buttons(self, frame):
        """시작 및 닫기 버튼을 설정합니다."""
        start_frame = Frame(frame)
        start_frame.pack(expand=True, fill='both')

        self.start_button = Button(
            start_frame,
            text="작업 시작",
            font=default_font,
            command=self.start_task
        )
        self.start_button.pack(fill='both', expand=True)

        close_frame = Frame(frame)
        close_frame.pack(expand=True, fill='both')

        close_button = Button(close_frame, text="닫기", font=default_font, command=self.close_window)
        close_button.pack(fill='both', expand=True)

    def load_excel_data(self):
        """엑셀 파일을 읽어 COLUMN_BEFORE 확인 및 총 데이터 표시."""
        try:
            self._verify_excel_columns()
            total_rows = len(self.df)
            self.status_var.set(f"총 데이터 개수: {total_rows}")
        except Exception as e:
            self.show_error(f"엑셀 파일 읽기 오류: {str(e)}")

    def _verify_excel_columns(self):
        """엑셀 열을 확인합니다."""
        if COLUMN_BEFORE not in self.df.columns:
            self.show_error(f"엑셀 파일에 {COLUMN_BEFORE} 열이 없습니다.")
            self.window_a.destroy()

    def start_task(self):
        """작업을 시작하고 버튼을 비활성화."""
        self.start_button.config(state='disabled')
        self.stop_event.clear()
        Thread(target=self.run_in_thread).start()

    def run_in_thread(self):
        """새 쓰레드에서 이벤트 루프 실행."""
        asyncio.run(self.process_text(self.file_path, self.update_queue))

    async def process_text(self, file_path, update_queue):
        """엑셀 파일 처리 및 HTTP POST 요청."""
        if self.df is None:
            self.show_error("데이터가 로드되지 않았습니다.")
            return

        self.df[COLUMN_AFTER] = ""
        if COLUMN_STATUS not in self.df.columns:
            self.df[COLUMN_STATUS] = ""
        total_rows = len(self.df)

        async with aiohttp.ClientSession() as session:
            await self._process_rows(session, total_rows, file_path)

    async def _process_rows(self, session, total_rows, file_path):
        """각 행을 처리합니다."""
        try:
            for idx, row in self.df.iterrows():
                if self.stop_event.is_set():
                    self.update_queue.put(("작업이 중단되었습니다.", 0))
                    return

                if self.df.at[idx, COLUMN_STATUS] == PLAG_STATUS_SUCCESS:
                    await self._update_progress(idx, total_rows)  # 비동기 호출
                    continue

                sha_256 = sha_256_hash()
                data = {"hash": sha_256, "content": row[COLUMN_BEFORE]}
                success, message = await self._send_request_with_error_handling(session, data)

                self.df.at[idx, COLUMN_AFTER] = message

                if success:
                    self.df.at[idx, COLUMN_STATUS] = PLAG_STATUS_SUCCESS
                else:
                    self.df.at[idx, COLUMN_STATUS] = PLAG_STATUS_FAIL

                self.df.to_excel(file_path, index=False)  # 즉시 결과 저장

                await self._update_progress(idx, total_rows)  # 비동기 호출
        except PermissionError as e:
            self.show_error("파일이 다른 프로그램에서 열려 있습니다.")
            return

    async def _send_request_with_error_handling(self, session, data):
        """HTTP POST 요청을 전송하고 오류를 처리합니다."""
        try:
            response = await self.send_post_request(session, data)
            success = response["success"]
            message = response["message"]

            if success:
                return success, message
            else:
                self.show_error(message)
                raise Exception(message)

        except aiohttp.ClientError as e:
            self.stop_event.set()
            return False, f"클라이언트 오류: {str(e)}"
        except asyncio.TimeoutError:
            self.stop_event.set()
            return False, "요청 시간이 초과되었습니다."
        except Exception as e:
            self.stop_event.set()
            return False, f"오류: {str(e)}"

    async def send_post_request(self, session, data):
        """HTTP POST 요청을 보내는 함수."""
        url = API_URL
        async with session.post(url, json=data) as response:
            if response.status != 200:
                raise Exception(f"HTTP {response.status}")
            return await response.json()

    async def _update_progress(self, idx, total_rows):
        """진행률을 업데이트합니다."""
        progress_value = (idx + 1) / total_rows * 100
        self.update_queue.put((f"진행 중: {idx + 1}/{total_rows} 처리 완료", progress_value))
        await asyncio.sleep(0.1)  # 비동기 대기 추가

    def update_status(self):
        """큐에서 메시지를 꺼내 상태 업데이트."""
        try:
            while True:
                message, progress_value = self.update_queue.get_nowait()
                self.status_var.set(message)
                self.progress["value"] = progress_value

                if progress_value >= 100:
                    self.status_var.set("작업이 완료되었습니다.")
                    break
        except Empty:
            self.window_a.after(100, self.update_status)

    def close_window(self):
        """창을 닫을 때 호출되는 함수."""
        self.stop_event.set()
        self.window_a.destroy()

    def show_error(self, message):
        """오류 메시지를 표시합니다."""
        messagebox.showerror("오류", message)
