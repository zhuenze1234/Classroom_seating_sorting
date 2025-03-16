# main.py
from ui import WinGUI
from control import Controller

if __name__ == "__main__":
    root = WinGUI()
    controller = Controller()
    controller.init(root)
    root.mainloop()