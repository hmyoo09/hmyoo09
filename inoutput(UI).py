# main.py
import importlib.util
import sys
import site
import gradio as gr
import os
import json
import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError
import ast
from playsound import playsound
import sys
import importlib.util
import os
import time
import pyautogui
from datetime import datetime

def capture_screen_to_file():
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path =f"./gradio_live_capture_{timestamp}.png"

        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)

        print(f"화면 캡처 완료: {screenshot_path}")
        return f"화면 캡처 완료! 저장 위치: {screenshot_path}"
    except Exception as e:
        print(f"[캡처 실패] {e}")
        return f"캡처 실패: {e}"

def is_stdlib_module(module_name):
    try:
        # 1. import 가능한지 확인
        spec = importlib.util.find_spec(module_name)
        if spec is None or spec.origin is None:
            return False
        
        # 2. 경로가 없으면 built-in (예: math, sys 등)
        if spec.origin == 'built-in':
            return True
        
        # 3. 표준 라이브러리 경로 확인
        stdlib_path = os.path.abspath(os.path.dirname(os.__file__))  # ex: /usr/lib/python3.10/
        module_path = os.path.abspath(spec.origin)
        return module_path.startswith(stdlib_path)
    except Exception:
        return False


def is_pypi_module(module_name):
    try:
        # 모듈 스펙 가져오기
        spec = importlib.util.find_spec(module_name)
        if spec is None or spec.origin is None:
            return False  # import 자체가 불가능한 경우

        module_path = os.path.abspath(spec.origin)
        site_paths = site.getsitepackages() + [site.getusersitepackages()]

        # PyPI 설치 경로 내부에 있는지 확인
        return any(module_path.startswith(os.path.abspath(site_path)) for site_path in site_paths)
    except Exception as e:
        return False

def play_start_sound():
    try:
        playsound("efan.wav")  # 🎵 시작 알림 사운드
    except Exception as e:
        print(f"알림음 재생 실패: {e}")


def sound():
    try:
        playsound("beep-03.wav")
    except Exception as audio_err:
        print(f"소리 재생 실패: {audio_err}")

def check_module(string):
    not_available=['google','%','%%']
    for word in not_available:
        if word in string:
            return False
    return True

def del_pound(string):    
    if '#' in string:
        idx_an=string.find('#')
        return string[:idx_an]
    else:
        return string

def extract_imports(source_code: str):
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return "", []

    lines = source_code.splitlines()
    import_lines = []
    un_imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modname = alias.name.split('.')[0]
                asname = alias.asname or alias.name
                asname=asname if asname else ''
                if is_pypi_module(modname) or is_stdlib_module(modname):
                    import_lines.append(lines[node.lineno - 1].strip())
                else:
                    un_imports.append((alias.name, asname))

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modname = node.module.split('.')[0]
                for alias in node.names:
                    full_name = f"{node.module}.{alias.name}"
                    asname = alias.asname or alias.name
                    asname=asname if asname else ''
                if is_pypi_module(modname) or is_stdlib_module(modname):
                    import_lines.append(lines[node.lineno - 1].strip())
                else:
                    un_imports.append((full_name, asname))

    return '\n'.join(import_lines), un_imports

def extract_functions(source_code:str):
    func_dict = {}

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        # 파싱 실패 시 빈 dict 반환
        return func_dict

    # 소스 코드를 줄 단위 리스트로 준비
    lines = source_code.splitlines()

    for node in tree.body:
        if isinstance(node, ast.FunctionDef): # ast.FunctionDef가 함수의 정의 부분
            # 함수가 차지하는 줄 범위 구하기
            # lineno, end_lineno는 3.8+부터 지원
            start = node.lineno - 1  # 0-based index
            end = node.end_lineno    # end_lineno는 포함되는 마지막 줄 번호
            
            # 함수 코드 줄만 슬라이싱
            func_lines=[]
            for line in lines[start:end]:
                func_lines.append(del_pound(line))
            func_code = '\n'.join(func_lines)

            func_dict[node.name] = func_code

    return func_dict

def extract_variable_definitions(source_code: str):
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        sound()
        return {}

    lines = source_code.splitlines()
    var_defs = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            line = lines[node.lineno - 1].strip()
            targets = node.targets
            for target in targets:
                if isinstance(target, ast.Name):
                    var_defs[target.id] = line
                elif isinstance(target, ast.Tuple):
                    for elt in target.elts:
                        if isinstance(elt, ast.Name):
                            var_defs[elt.id] = line

    return var_defs

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
            sound()
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
        sound()
        return "text파일이 정상적으로 만들어지지 않았습니다."

    for line in lines:
        if any(word in line for word in ToDoWords):
            ToDoList.append(line.strip())

    if len(ToDoList)!=0:
        return '\n'.join([f"{i+1}. {ToDoList[i]}" for i in range(len(ToDoList))])
    else:
        return '고칠 부분이 없습니다.'

def find_error(ipynb_path):
    just_errors=''
    errors_but_ok=''
    module_not_found=[]
    ok_to_make_error=False
    needed_libs=''
    needed_funcs={}
    needed_varis={}
    need_inputs=''
    with open(ipynb_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    for i, cell in enumerate(nb.cells):
        if cell.cell_type != 'code':
            if cell.cell_type=='markdown':
                if 'Error' in cell['source']:
                    ok_to_make_error=True
            continue
        
        if not check_module(cell['source']):
            continue
        
        if 'input' in cell['source']:
            need_inputs+='\n'+f'Cell {i+1} input이 필요함'
            continue

        try:
            in_cell_funcs=extract_functions(cell['source'])
        except TypeError:
            in_cell_funcs=extract_functions('\n'.join(cell['source']))
        
        try:
            needed_funcs.update(in_cell_funcs)
        except: pass

        try:
            in_cell_varis=extract_variable_definitions(cell['source'])
        except TypeError:
            in_cell_varis=extract_variable_definitions('\n'.join(cell['source']))
        
        try:
            needed_varis.update(in_cell_varis)
        except: pass

        result = extract_imports(cell['source'])
        add_libs, un_imports = result if isinstance(result, tuple) and len(result) == 2 else ("", [])
        needed_libs+='\n'+add_libs
        module_not_found+=un_imports

        tmp=False
        for names in module_not_found:
            if names[0] in cell['source']:
                idx=cell['source'].find(names[0])
                if cell['source'][idx+len(names[0])]=='.':
                    tmp=True
                    break
            if names[1] in cell['source']:
                idx=cell['source'].find(names[1])
                if cell['source'][idx+len(names[1])]=='.':
                    tmp=True
                    break

        if tmp:
            continue


        tmp=False
        for line in cell['source'].split('\n'):
            if '#' in line and 'Error' in line:
                tmp=True
                break

        if tmp:
            ok_to_make_error=True
        
        for func_name,func_content in needed_funcs.items():
            if func_name in in_cell_funcs:
                continue
            else:
                if func_name in cell['source']:
                    cell['source']=''.join(concat_sources(func_content,cell['source']))
                    '''
                    if cell['source'][cell['source'].find(func_name)+len(func_name)]=='(':
                        cell['source']=''.join(concat_sources(func_content,cell['source']))
                    '''

        for vari_name,vari_content in needed_varis.items():
            if vari_name in in_cell_varis:
                continue
            if vari_name in cell['source']:
                cell['source']=''.join(concat_sources(vari_content,cell['source']))

        cell['source']=''.join(concat_sources(needed_libs,cell['source']))
        #print(cell['source'])

        single_cell_nb = nbformat.v4.new_notebook(cells=[cell])
        try:
            #print(f"\Cell {i+1} 실행 중...")
            client = NotebookClient(single_cell_nb, timeout=20, kernel_name='python3')
            client.execute()
            #print(f"Cell {i+1} 성공")
        except CellExecutionError as e:
            #print(f"Cell {i+1} 실패: {e.ename} - {e.evalue}")
            if not ok_to_make_error:
                just_errors+='\n'+f'Cell {i+1} 실패: {e.ename} - {e.evalue}'
            else:
                errors_but_ok+='\n'+f'Cell {i+1} 에러명 이거 맞지?: {e.ename} - {e.evalue}'
                ok_to_make_error=False

    if module_not_found:
        mo='\n'.join([f'모듈:{tup[0]} 별칭:{tup[1]}' for tup in module_not_found])
    else:
        mo='해당사항 없음'
    
    #print(in_cell_funcs)
    #print(needed_funcs)

    return just_errors, errors_but_ok, mo, need_inputs
    
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
        module_errors=gr.Textbox(label='모듈을 못잧겠음',interactive=False)
        need_inputs=gr.Textbox(label='이건 직접 입력해서 테스트 ㄱㄱ', interactive=False)

        file_input.change(
            fn=show_UI,
            inputs=file_input,
            outputs=[output_text, finding, errors, errors_but_ok,module_errors,need_inputs]
        )
        capture_btn = gr.Button("현재 브라우저 화면 캡처하기")
        capture_result = gr.Textbox(label="캡처 결과", interactive=False)

        capture_btn.click(fn=capture_screen_to_file, outputs=capture_result)
        play_start_sound() 

    iface.launch(server_name="127.0.0.1", server_port=7860)

if __name__=='__main__':
    main()
