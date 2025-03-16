# main.py
from ui import WinGUI  # 确保从ui模块导入正确的窗口类
from control import Controller

if __name__ == "__main__":
    # 初始化界面
    win = WinGUI()  # 直接使用WinGUI实例

    # 初始化控制器
    controller = Controller()

    # 绑定控制器到UI
    controller.init(win)  # 将win实例传递给控制器

    # 启动主循环
    win.mainloop()