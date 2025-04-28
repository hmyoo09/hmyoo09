import json
import os
import tkinter as tk
from tkinter import filedialog
import sys


def main():
    # 1. tkinter 기본 창 숨기기
    root = tk.Tk()
    root.withdraw()

    # 2. 파일 선택 다이얼로그 열기
    input_path = filedialog.askopenfilename(
        title="변환할 .ipynb 파일을 선택하세요",
        filetypes=[("IPython Notebook", "*.ipynb")]
    )

    # 파일 선택 여부 확인
    if not input_path:
        print("파일을 선택하지 않았습니다.")
        return
    
    # 3. JSON 파일 로드
    with open(input_path, 'r', encoding='utf-8') as f:
        notebook_data = json.load(f)

    # 4. JSON 문자열로 변환
    json_as_text = json.dumps(notebook_data, indent=2, ensure_ascii=False)

    # 5. 바탕화면(Desktop) 경로 가져오기
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    output_path = os.path.join(desktop_path, 'tt.txt')

    # 6. 변환된 텍스트 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(json_as_text)

    print(f"변환된 파일이 바탕화면에 저장되었습니다: {output_path}")

if __name__ == "__main__":
    main()
