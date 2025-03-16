"""
本代码由[Tkinter布局助手]生成
官网:https://www.pytk.net
QQ交流群:905019785
在线反馈:https://support.qq.com/product/618914
"""
import random
from tkinter import *
from tkinter.ttk import *


class WinGUI(Tk):
    def __init__(self):
        super().__init__()
        self.__win()
        self.tk_tabs_m8acommq = self.__tk_tabs_m8acommq(self)
        self.tk_table_m8awzxkt = self.__tk_table_m8awzxkt(self.tk_tabs_m8acommq_0)
        self.tk_label_m8b8r2at = self.__tk_label_m8b8r2at(self.tk_tabs_m8acommq_2)
        self.tk_label_m8b8sfeg = self.__tk_label_m8b8sfeg(self.tk_tabs_m8acommq_2)
        self.tk_input_m8b8y7zs = self.__tk_input_m8b8y7zs(self.tk_tabs_m8acommq_0)
        self.tk_label_m8b8yc3e = self.__tk_label_m8b8yc3e(self.tk_tabs_m8acommq_0)
        self.tk_button_m8b8z6uo = self.__tk_button_m8b8z6uo(self.tk_tabs_m8acommq_0)
        self.tk_label_m8b9092q = self.__tk_label_m8b9092q(self.tk_tabs_m8acommq_0)
        self.tk_progressbar_m8b910ks = self.__tk_progressbar_m8b910ks(self.tk_tabs_m8acommq_0)
        self.tk_label_m8b918w9 = self.__tk_label_m8b918w9(self.tk_tabs_m8acommq_0)
        self.tk_scale_m8b91zcg = self.__tk_scale_m8b91zcg(self.tk_tabs_m8acommq_0)
        self.tk_input_m8b925pn = self.__tk_input_m8b925pn(self.tk_tabs_m8acommq_0)
        self.tk_text_m8b930ud = self.__tk_text_m8b930ud(self.tk_tabs_m8acommq_0)
        self.tk_label_m8b937sx = self.__tk_label_m8b937sx(self.tk_tabs_m8acommq_0)
        self.tk_button_m8b9519y = self.__tk_button_m8b9519y(self.tk_tabs_m8acommq_0)
        self.tk_button_m8b95daa = self.__tk_button_m8b95daa(self.tk_tabs_m8acommq_0)
        self.tk_input_m8b95r63 = self.__tk_input_m8b95r63(self.tk_tabs_m8acommq_0)
        self.tk_label_m8b95w3k = self.__tk_label_m8b95w3k(self.tk_tabs_m8acommq_0)
        self.tk_button_m8b96nxu = self.__tk_button_m8b96nxu(self.tk_tabs_m8acommq_0)
        self.tk_button_m8b9721p = self.__tk_button_m8b9721p(self.tk_tabs_m8acommq_0)
        self.tk_text_m8b9c2kt = self.__tk_text_m8b9c2kt(self.tk_tabs_m8acommq_1)
        self.tk_label_m8b9lfec = self.__tk_label_m8b9lfec(self.tk_tabs_m8acommq_1)
        self.tk_select_box_m8b9m8kp = self.__tk_select_box_m8b9m8kp(self.tk_tabs_m8acommq_1)
        self.tk_label_m8b9ml9m = self.__tk_label_m8b9ml9m(self.tk_tabs_m8acommq_1)
        self.tk_text_m8b9mw1x = self.__tk_text_m8b9mw1x(self.tk_tabs_m8acommq_1)
        self.tk_label_m8b9ncr5 = self.__tk_label_m8b9ncr5(self.tk_tabs_m8acommq_1)
        self.tk_label_m8b9rtjn = self.__tk_label_m8b9rtjn(self.tk_tabs_m8acommq_1)
        self.tk_input_m8b9sdst = self.__tk_input_m8b9sdst(self.tk_tabs_m8acommq_1)
        self.tk_button_m8b9siwe = self.__tk_button_m8b9siwe(self.tk_tabs_m8acommq_1)

    def __win(self):
        self.title("class seating 教室排序助手")
        # 设置窗口大小、居中
        width = 600
        height = 500
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)

        self.resizable(width=False, height=False)

    def scrollbar_autohide(self, vbar, hbar, widget):
        """自动隐藏滚动条"""

        def show():
            if vbar: vbar.lift(widget)
            if hbar: hbar.lift(widget)

        def hide():
            if vbar: vbar.lower(widget)
            if hbar: hbar.lower(widget)

        hide()
        widget.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Leave>", lambda e: hide())
        if hbar: hbar.bind("<Enter>", lambda e: show())
        if hbar: hbar.bind("<Leave>", lambda e: hide())
        widget.bind("<Leave>", lambda e: hide())

    def v_scrollbar(self, vbar, widget, x, y, w, h, pw, ph):
        widget.configure(yscrollcommand=vbar.set)
        vbar.config(command=widget.yview)
        vbar.place(relx=(w + x) / pw, rely=y / ph, relheight=h / ph, anchor='ne')

    def h_scrollbar(self, hbar, widget, x, y, w, h, pw, ph):
        widget.configure(xscrollcommand=hbar.set)
        hbar.config(command=widget.xview)
        hbar.place(relx=x / pw, rely=(y + h) / ph, relwidth=w / pw, anchor='sw')

    def create_bar(self, master, widget, is_vbar, is_hbar, x, y, w, h, pw, ph):
        vbar, hbar = None, None
        if is_vbar:
            vbar = Scrollbar(master)
            self.v_scrollbar(vbar, widget, x, y, w, h, pw, ph)
        if is_hbar:
            hbar = Scrollbar(master, orient="horizontal")
            self.h_scrollbar(hbar, widget, x, y, w, h, pw, ph)
        self.scrollbar_autohide(vbar, hbar, widget)

    def __tk_tabs_m8acommq(self, parent):
        frame = Notebook(parent)
        self.tk_tabs_m8acommq_0 = self.__tk_frame_m8acommq_0(frame)
        frame.add(self.tk_tabs_m8acommq_0, text="座位排序")
        self.tk_tabs_m8acommq_1 = self.__tk_frame_m8acommq_1(frame)
        frame.add(self.tk_tabs_m8acommq_1, text="人员录入")
        self.tk_tabs_m8acommq_2 = self.__tk_frame_m8acommq_2(frame)
        frame.add(self.tk_tabs_m8acommq_2, text="作者")
        frame.place(x=0, y=0, width=598, height=500)
        return frame

    def __tk_frame_m8acommq_0(self, parent):
        frame = Frame(parent)
        frame.place(x=0, y=0, width=598, height=500)
        return frame

    def __tk_frame_m8acommq_1(self, parent):
        frame = Frame(parent)
        frame.place(x=0, y=0, width=598, height=500)
        return frame

    def __tk_frame_m8acommq_2(self, parent):
        frame = Frame(parent)
        frame.place(x=0, y=0, width=598, height=500)
        return frame

    def __tk_table_m8awzxkt(self, parent):
        # 表头字段 表头宽度
        columns = {"ID": 119, "字段#1": 179, "字段#2": 298}
        tk_table = Treeview(parent, show="headings", columns=list(columns), )
        for text, width in columns.items():  # 批量设置列属性
            tk_table.heading(text, text=text, anchor='center')
            tk_table.column(text, anchor='center', width=width, stretch=False)  # stretch 不自动拉伸

        tk_table.place(x=0, y=188, width=598, height=228)
        return tk_table

    def __tk_label_m8b8r2at(self, parent):
        label = Label(parent, text="作者：朱恩泽", anchor="center", )
        label.place(x=184, y=162, width=232, height=40)
        return label

    def __tk_label_m8b8sfeg(self, parent):
        label = Label(parent, text="项目地址：https://github.com/zhuenze1234/Classroom_seating_sorting",
                      anchor="center", )
        label.place(x=88, y=200, width=423, height=68)
        return label

    def __tk_input_m8b8y7zs(self, parent):
        ipt = Entry(parent, )
        ipt.place(x=52, y=3, width=150, height=30)
        return ipt

    def __tk_label_m8b8yc3e(self, parent):
        label = Label(parent, text="种子", anchor="center", )
        label.place(x=0, y=2, width=51, height=30)
        return label

    def __tk_button_m8b8z6uo(self, parent):
        btn = Button(parent, text="随机种子", takefocus=False, )
        btn.place(x=209, y=0, width=50, height=30)
        return btn

    def __tk_label_m8b9092q(self, parent):
        label = Label(parent, text="线程数", anchor="center", )
        label.place(x=0, y=39, width=248, height=30)
        return label

    def __tk_progressbar_m8b910ks(self, parent):
        progressbar = Progressbar(parent, orient=HORIZONTAL, )
        progressbar.place(x=0, y=152, width=595, height=30)
        return progressbar

    def __tk_label_m8b918w9(self, parent):
        label = Label(parent, text="进度", anchor="center", )
        label.place(x=274, y=118, width=50, height=30)
        return label

    def __tk_scale_m8b91zcg(self, parent):
        scale = Scale(parent, orient=HORIZONTAL, )
        scale.place(x=0, y=73, width=138, height=30)
        return scale

    def __tk_input_m8b925pn(self, parent):
        ipt = Entry(parent, )
        ipt.place(x=140, y=74, width=68, height=30)
        return ipt

    def __tk_text_m8b930ud(self, parent):
        text = Text(parent)
        text.place(x=381, y=34, width=217, height=117)
        return text

    def __tk_label_m8b937sx(self, parent):
        label = Label(parent, text="日志", anchor="center", )
        label.place(x=463, y=0, width=50, height=30)
        return label

    def __tk_button_m8b9519y(self, parent):
        btn = Button(parent, text="确定", takefocus=False, )
        btn.place(x=218, y=75, width=50, height=30)
        return btn

    def __tk_button_m8b95daa(self, parent):
        btn = Button(parent, text="开始", takefocus=False, )
        btn.place(x=20, y=434, width=50, height=30)
        return btn

    def __tk_input_m8b95r63(self, parent):
        ipt = Entry(parent, )
        ipt.place(x=194, y=434, width=166, height=30)
        return ipt

    def __tk_label_m8b95w3k(self, parent):
        label = Label(parent, text="结果保存路径", anchor="center", )
        label.place(x=110, y=434, width=83, height=30)
        return label

    def __tk_button_m8b96nxu(self, parent):
        btn = Button(parent, text="选择", takefocus=False, )
        btn.place(x=365, y=434, width=50, height=30)
        return btn

    def __tk_button_m8b9721p(self, parent):
        btn = Button(parent, text="确定", takefocus=False, )
        btn.place(x=426, y=434, width=50, height=30)
        return btn

    def __tk_text_m8b9c2kt(self, parent):
        text = Text(parent)
        text.place(x=0, y=33, width=155, height=440)
        return text

    def __tk_label_m8b9lfec(self, parent):
        label = Label(parent, text="当前同学", anchor="center", )
        label.place(x=105, y=0, width=50, height=30)
        return label

    def __tk_select_box_m8b9m8kp(self, parent):
        cb = Combobox(parent, state="readonly", )
        cb['values'] = ("列表框", "Python", "Tkinter Helper")
        cb.place(x=314, y=0, width=150, height=30)
        return cb

    def __tk_label_m8b9ml9m(self, parent):
        label = Label(parent, text="当前班级", anchor="center", )
        label.place(x=0, y=0, width=50, height=30)
        return label

    def __tk_text_m8b9mw1x(self, parent):
        text = Text(parent)
        text.place(x=53, y=0, width=48, height=30)
        return text

    def __tk_label_m8b9ncr5(self, parent):
        label = Label(parent, text="选择班级", anchor="center", )
        label.place(x=254, y=0, width=50, height=30)
        return label

    def __tk_label_m8b9rtjn(self, parent):
        label = Label(parent, text="加入同学", anchor="center", )
        label.place(x=254, y=63, width=50, height=30)
        return label

    def __tk_input_m8b9sdst(self, parent):
        ipt = Entry(parent, )
        ipt.place(x=307, y=62, width=150, height=30)
        return ipt

    def __tk_button_m8b9siwe(self, parent):
        btn = Button(parent, text="确定", takefocus=False, )
        btn.place(x=461, y=58, width=50, height=30)
        return btn


class Win(WinGUI):
    def __init__(self, controller):
        self.ctl = controller
        super().__init__()
        self.__event_bind()
        self.__style_config()
        self.ctl.init(self)

    def __event_bind(self):
        pass

    def __style_config(self):
        pass


if __name__ == "__main__":
    win = WinGUI()
    win.mainloop()