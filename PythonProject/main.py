
import json

def new_student():
    with open('students.json', 'w', encoding='utf-8') as f:
        student = {}
        a=input("please enter student name:\nif you want quit press enter 'q'")
        while True:
            if a == 'q':
                break
            else:
                student[a]=int(input("please enter student level(level high is good student,low is bad student):"))
        print("student data is ok,please wait a moment...")
        f.write(json.dumps(student))


def input_data(ulr,mode='r'):
    try:
        with open(ulr, mode) as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print('File not found\nPlease add the student')
        new_student()

def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 Ctrl+F8 切换断点。


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':

    input_data("./data/data.json")
    print_hi('PyCharm')
