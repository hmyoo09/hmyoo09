# main.py
import os
import threading
import nest_asyncio
from inoutput_tkinter import *
from inoutput_gradio import *

def main():
    nest_asyncio.apply()
    try:
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        text_path = os.path.join(desktop_path, 'tt.txt')
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write('')
    except:
        pass

    # Gradio 실행을 백그라운드 쓰레드로
    threading.Thread(target=launch_gradio, daemon=True).start()

    # Tkinter는 반드시 메인 스레드에서 실행
    start_tkinter()


if __name__=='__main__':
    main()