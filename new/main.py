# main.py
import os
import sys
import subprocess
from importlib import util
from ui import WinGUI
from control import Controller


# 需要安装的第三方库
REQUIRED_LIBRARIES = [
    ('numpy', 'numpy'),
    ('pandas', 'pandas'),
    ('openpyxl', 'openpyxl'),
    ('tqdm', 'tqdm'),
    ('queue', 'queue')
]


def install_dependencies():
    missing = []
    for (import_name, pkg_name) in REQUIRED_LIBRARIES:
        if not util.find_spec(import_name):
            missing.append(pkg_name)

    if missing:
        print("首次运行需要安装依赖库...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
            print("依赖安装完成！")
        except Exception as e:
            print(f"安装失败：{str(e)}")
            sys.exit(1)



# 主程序
if __name__ == "__main__":
    # 检查依赖
    try:
        import numpy
        import pandas
        from tkinter import ttk
    except ImportError:
        print("正在自动安装依赖...")
        install_dependencies()

    # 启动主程序

    root = WinGUI()
    controller = Controller()
    controller.init(root)
    root.mainloop()