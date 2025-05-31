import gradio as gr
import os
import json

def file_upload_maketxt(file):
    if file is None:
        raise gr.Error("파일이 존재하지 않습니다.")
    file_path=file.name
    file_size=os.path.getsize(file_path)
    
    with open(file.name, 'r', encoding='utf-8') as f:
        notebook_data = json.load(f)

    json_as_text = json.dumps(notebook_data, indent=2, ensure_ascii=False)

    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    output_path = os.path.join(desktop_path, 'tt.txt')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(json_as_text)

    return f"파일명: {file_path}\n크기: {file_size} bytes\n\n" \
           f"tt.txt가 바탕화면에 저장되었습니다:\n{output_path}"



iface = gr.Interface(
    fn=file_upload_maketxt,
    inputs=gr.File(label="ipynb 파일 업로드",file_types=['.ipynb']),
    outputs="text",
    title="코랩 암살 피하기!",
    description="ipynb 파일을 업로드하면 바탕화면에 tt.txt로 저장해드립니다.",
    allow_flagging="never",
)

iface.launch(share=True)
