import gradio as gr
import os
import json

def find_empty_space(text_path):
    ToDoWords = ['#code:', '설명', '아래에 코드 작성']
    ToDoList = []

    try:
        with open(text_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return "text파일이 정상적으로 만들어지지 않았습니다."

    for line in lines:
        if any(word in line for word in ToDoWords):
            ToDoList.append(line.strip()+'=>'+f' {1}번째 Cell')

    if len(ToDoList)!=0:
        return '\n'.join([f"{i+1}. {ToDoList[i]}" for i in range(len(ToDoList))])
    else:
        return '고칠 부분이 없습니다.'

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

    info_str = f"파일명: {file_path}\n크기: {file_size} bytes\n\n"+f"tt.txt가 바탕화면에 저장되었습니다:\n{output_path}"

    return info_str, todo_text

def main():
    # 기존 tt.txt 내용 초기화
    try:
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        text_path = os.path.join(desktop_path, 'tt.txt')
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write('')
    except:
        pass
    
        
    with gr.Blocks() as iface:
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        text_path = os.path.join(desktop_path, 'tt.txt')
        gr.Markdown("# 코랩 암살 피하기!")

        file_input = gr.File(label="ipynb 파일 업로드", file_types=['.ipynb'])
        output_text = gr.Textbox(label='파일 경로와 크기', interactive=False)
        finding = gr.Textbox(label='고칠 부분', interactive=False)

        file_input.change(
            fn=show_UI,
            inputs=file_input,
            outputs=[output_text, finding]
        )

    iface.launch()

main()
