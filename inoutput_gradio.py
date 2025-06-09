import gradio as gr
import os, json
from soundimage import *
from emptycell import *
from wrongcode import *
import soundimage as si


def show_UI(file):
    if file is None:
        sound()
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

    errors,errors_but_ok,module_errors,need_inputs=find_error(file_path)

    todo_text = find_empty_space(output_path)

    info_str = f"파일명: {file_path}\n크기: {file_size} bytes\n\n"+f"tt.txt가 바탕화면에 저장되었습니다:\n{output_path}"
    return info_str, todo_text, errors, errors_but_ok ,module_errors,need_inputs

def launch_gradio():
    with gr.Blocks() as iface:
        gr.Markdown("# 코랩 암살 피하기!")

        file_input = gr.File(label="ipynb 파일 업로드", file_types=['.ipynb'])
        output_text = gr.Textbox(label='파일 경로와 크기', interactive=False)
        finding = gr.Textbox(label='고칠 부분', interactive=False)
        errors = gr.Textbox(label='에러난 부분', interactive=False)
        errors_but_ok = gr.Textbox(label='에러나도 되는 부분', interactive=False)
        module_errors = gr.Textbox(label='모듈을 못잧겠음', interactive=False)
        need_inputs = gr.Textbox(label='이건 직접 입력해서 테스트 ㄱㄱ', interactive=False)

        file_input.change(
            fn=show_UI,
            inputs=file_input,
            outputs=[output_text, finding, errors, errors_but_ok, module_errors, need_inputs]
        )

        capture_btn = gr.Button("현재 브라우저 화면 캡처하기")
        capture_result = gr.Textbox(label="캡처 결과", interactive=False)
        capture_btn.click(fn=si.capture_screen_to_file, outputs=capture_result)

        play_start_sound()
        iface.launch(server_name="127.0.0.1", server_port=7860)
