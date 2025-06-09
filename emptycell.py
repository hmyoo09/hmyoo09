from soundimage import *

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
