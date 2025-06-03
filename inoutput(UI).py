import gradio as gr
import os
import json
import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

def del_pound(string):
    try:
        idx_an=string.find('#')
        return string[:idx_an]
    except:
        return string
        

def concat_sources(src1, src2):
    # src1, src2는 str 또는 list[str] 가능
    # 둘 다 리스트로 변환 후 합쳐서 리턴
    def to_list(src):
        if isinstance(src, str):
            # 빈 문자열이면 빈 리스트로 처리
            return [] if src.strip() == '' else [line + '\n' for line in src.splitlines()]
        elif isinstance(src, list):
            # 이미 리스트면 그대로 리턴, 단 각 줄에 \n 없으면 붙이기
            return [line if line.endswith('\n') else line + '\n' for line in src]
        else:
            raise TypeError(f"Unsupported source type: {type(src)}")

    list1 = to_list(src1)
    list2 = to_list(src2)
    return list1 + list2


def find_empty_space(text_path):
    ToDoWords = ['#code', '설명', '아래에 코드 작성']
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

def find_error(ipynb_path):
    just_errors=''
    errors_but_ok=''
    ok_to_make_error=False
    needed_libs=''
    needed_funcs={}
    with open(ipynb_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    for i, cell in enumerate(nb.cells):
        if cell.cell_type != 'code':
            if cell.cell_type=='markdown':
                if 'Error' in cell['source']:
                    ok_to_make_error=True
            continue
        
        tmp=False
        in_func=False
        func_content=''
        in_cell_funcs={}
        for line in cell['source'].split('\n'):
            if 'import' in line:
                needed_libs=needed_libs+line+'\n'
            if 'def' in line:
                in_func=True
                func_name=''
                func_define=''
                idx_def=''
                try:
                    idx_def=line.find('def')
                except: pass
                line=del_pound(line)
                try:
                    idx_first=line.find('(')
                    idx_last=line[::-1].find(')')
                    func_name=line[idx_def+3:idx_first].strip()
                    func_define=line[idx_first:idx_last+1]
                    if func_name not in needed_funcs:
                        needed_funcs[func_name] = {}
                    needed_funcs[func_name]['func_define'] = func_define
        
                    if func_name not in in_cell_funcs:
                        in_cell_funcs[func_name] = {}
                    in_cell_funcs[func_name]['func_define'] = func_define 
                except: pass
                func_content+=line
            if in_func:
                if '\t'==line[0:2]:
                    func_content+=line #여기서 안걸러지는 듯
                else:
                    needed_funcs[func_name]['func_content']=func_content
                    in_cell_funcs[func_name]['func_content']=func_content
                    func_content=''

        for line in cell['source'].split('\n'):
            if '#' in line and 'Error' in line:
                tmp=True
                break
        if tmp:
            ok_to_make_error=True
        
        cell['source']=''.join(concat_sources(needed_libs,cell['source']))
        for func_name,func in needed_funcs.items():
            if func_name in in_cell_funcs:
                if func['func_define']!=in_cell_funcs[func_name]['func_define']:
                    cell['source']=''.join(concat_sources(func['func_content'],cell['source']))
            else:
                cell['source']=''.join(concat_sources(func['func_content'],cell['source']))
        print(cell['source'])

        single_cell_nb = nbformat.v4.new_notebook(cells=[cell])
        try:
            print(f"\n📦 Cell {i+1} 실행 중...")
            client = NotebookClient(single_cell_nb, timeout=20, kernel_name='python3')
            client.execute()
            print(f"✅ Cell {i+1} 성공")
        except CellExecutionError as e:
            print(f"❌ Cell {i+1} 실패: {e.ename} - {e.evalue}")
            if not ok_to_make_error:
                just_errors+='\n'+f'Cell {i+1} 실패: {e.ename} - {e.evalue}'
            else:
                errors_but_ok+='\n'+f'Cell {i+1} 에러명 이거 맞지?: {e.ename} - {e.evalue}'
                ok_to_make_error=False
    
    return just_errors, errors_but_ok
    
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

    errors,errors_but_ok=find_error(file_path)

    todo_text = find_empty_space(output_path)

    info_str = f"파일명: {file_path}\n크기: {file_size} bytes\n\n"+f"tt.txt가 바탕화면에 저장되었습니다:\n{output_path}"

    return info_str, todo_text, errors, errors_but_ok

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
        errors=gr.Textbox(label='에러난 부분',interactive=False)
        errors_but_ok=gr.Textbox(label='에러나도 되는 부분',interactive=False)

        file_input.change(
            fn=show_UI,
            inputs=file_input,
            outputs=[output_text, finding, errors, errors_but_ok]
        )

    iface.launch()

main()
