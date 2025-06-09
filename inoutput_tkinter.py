import gradio as gr
import os
import json
import tkinter as tk
import webbrowser
import threading
import socket
import time

PORT = 7860
gradio_url = f"http://127.0.0.1:{PORT}"

def find_empty_space(text_path):
    ToDoWords = ['#code:', '설명', '아래에 코드 작성']
    ToDoList = []

    try:
        with open(text_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return "text파일이 정상적으로 만들어지지 않았습니다."

    for idx, line in enumerate(lines):
        if any(word in line for word in ToDoWords):
            ToDoList.append(line.strip() + f' => {idx + 1}번째 Cell')

    return '\n'.join([f"{i+1}. {ToDoList[i]}" for i in range(len(ToDoList))]) if ToDoList else '고칠 부분이 없습니다.'

def show_UI(file):
    if file is None:
        raise gr.Error("파일이 존재하지 않습니다.")
    
    file_path = file.name
    file_size = os.path.getsize(file_path)

    with open(file_path, 'r', encoding='utf-8') as f:
        notebook_data = json.load(f)
    json_as_text = json.dumps(notebook_data, indent=2, ensure_ascii=False)

    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    output_path = os.path.join(desktop_path, 'tt.txt')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(json_as_text)

    todo_text = find_empty_space(output_path)
    info_str = f"파일명: {file_path}\n크기: {file_size} bytes\n\ntt.txt가 바탕화면에 저장되었습니다:\n{output_path}"
    return info_str, todo_text

def launch_gradio():
    with gr.Blocks() as iface:
        gr.Markdown("# 코랩 암살 피하기!")
        file_input = gr.File(label="ipynb 파일 업로드", file_types=[".ipynb"])
        output_text = gr.Textbox(label="파일 경로와 크기", interactive=False)
        finding = gr.Textbox(label="고칠 부분", interactive=False)

        file_input.change(fn=show_UI, inputs=file_input, outputs=[output_text, finding])

    iface.launch(share=True, server_port=PORT, prevent_thread_lock=True, inbrowser=False)

def wait_for_port(port, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
    return False

def start_tkinter():
    root = tk.Tk()
    root.title("Gradio Launcher")
    root.geometry("400x160")
    root.attributes('-topmost', True)

    label = tk.Label(root, text="Launching Gradio...")
    label.pack(pady=10)

    link_label = tk.Label(root, text="(Waiting for URL...)", fg="gray", wraplength=380)
    link_label.pack(pady=5)

    button = tk.Button(root, text="Gradio 페이지로 이동하기", state="disabled")
    button.pack(pady=10)

    def wait_and_activate():
        if wait_for_port(PORT, timeout=10):
            root.after(0, lambda: [
                label.config(text="Gradio 서버가 실행되었습니다!"),
                link_label.config(text=gradio_url, fg="blue"),
                button.config(state="normal", command=lambda: webbrowser.open(gradio_url))
            ])
        else:
            root.after(0, lambda: label.config(text="Gradio 실행 실패. 포트를 열 수 없습니다.", fg="red"))

    threading.Thread(target=wait_and_activate, daemon=True).start()
    root.mainloop()

# 실행
if __name__ == "__main__":
    threading.Thread(target=launch_gradio, daemon=True).start()
    start_tkinter()
