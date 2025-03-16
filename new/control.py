# control.py
import threading
from tkinter import messagebox, filedialog
from service import ClassroomService
import random


class Controller:
    ui: object

    def __init__(self):
        self.service = ClassroomService()
        self.current_class = "default"
        self.running = False

    def init(self, ui):
        """初始化UI组件"""
        self.ui = ui

        # 绑定事件
        self.ui.tk_button_m8b8z6uo.config(command=self.generate_random_seed)
        self.ui.tk_button_m8b9519y.config(command=self.set_thread_count)
        self.ui.tk_button_m8b95daa.config(command=self.toggle_arrangement)
        self.ui.tk_button_m8b96nxu.config(command=self.select_output_path)
        self.ui.tk_button_m8b9721p.config(command=self.export_result)
        self.ui.tk_button_m8b9siwe.config(command=self.add_student)

        # 初始化控件
        self.ui.tk_scale_m8b91zcg.config(from_=1, to=8)
        self.ui.tk_scale_m8b91zcg.set(4)
        self.ui.tk_input_m8b925pn.insert(0, "4")
        self.ui.tk_input_m8b8y7zs.insert(0, str(random.randint(0, 10000)))
        self.ui.tk_input_m8b95r63.insert(0, "座位表.xlsx")

        # 加载班级数据
        self.load_classes()

    def load_classes(self):
        """加载已有班级列表"""
        classes = self.service.get_available_classes()
        self.ui.tk_select_box_m8b9m8kp['values'] = classes
        if classes:
            self.current_class = classes[0]
            self.load_current_class()

    def load_current_class(self):
        """加载当前班级数据"""
        try:
            students = self.service.load_class(self.current_class)
            self.update_student_table(students)
        except Exception as e:
            messagebox.showerror("错误", f"加载班级失败: {str(e)}")

    def update_student_table(self, students):
        """更新学生表格"""
        self.ui.tk_table_m8awzxkt.delete(*self.ui.tk_table_m8awzxkt.get_children())
        for idx, student in enumerate(students):
            self.ui.tk_table_m8awzxkt.insert("", "end",
                                             values=(idx + 1, student['name'], self.type_to_text(student['type'])))

    def type_to_text(self, t):
        """类型转文字说明"""
        return {
            1: "好学生",
            0: "普通学生",
            -1: "坏学生（4邻）",
            -2: "坏学生（8邻）"
        }.get(t, "未知")

    def generate_random_seed(self):
        """生成随机种子"""
        self.ui.tk_input_m8b8y7zs.delete(0, 'end')
        self.ui.tk_input_m8b8y7zs.insert(0, str(random.randint(0, 10 ** 6)))

    def set_thread_count(self):
        """设置线程数"""
        try:
            count = int(self.ui.tk_input_m8b925pn.get())
            if 1 <= count <= 8:
                self.ui.tk_scale_m8b91zcg.set(count)
            else:
                messagebox.showwarning("提示", "线程数范围1-8")
        except ValueError:
            messagebox.showerror("错误", "无效的线程数")

    def toggle_arrangement(self):
        """开始/停止排列"""
        if self.running:
            self.stop_arrangement()
        else:
            self.start_arrangement()

    def start_arrangement(self):
        """开始排列"""
        if not self.service.has_students():
            messagebox.showwarning("警告", "请先添加学生")
            return

        self.running = True
        self.ui.tk_button_m8b95daa.config(text="停止")
        self.ui.tk_progressbar_m8b910ks['value'] = 0
        self.log("开始计算座位排列...")

        # 获取参数
        seed = self.ui.tk_input_m8b8y7zs.get()
        thread_num = self.ui.tk_scale_m8b91zcg.get()

        # 启动线程
        self.worker_thread = threading.Thread(
            target=self.run_arrangement,
            args=(seed, thread_num),
            daemon=True
        )
        self.worker_thread.start()

    def stop_arrangement(self):
        """停止排列"""
        self.running = False
        self.service.stop()
        self.ui.tk_button_m8b95daa.config(text="开始")
        self.log("已停止计算")

    def run_arrangement(self, seed, thread_num):
        """运行排列算法"""
        try:
            result = self.service.arrange(
                seed=seed,
                thread_num=thread_num,
                progress_callback=self.update_progress,
                log_callback=self.log
            )

            if result:
                self.log(f"成功找到排列方案！种子：{result['seed']}")
                self.service.current_result = result
            else:
                self.log("未找到有效排列方案")

        except Exception as e:
            self.log(f"发生错误：{str(e)}")
        finally:
            self.running = False
            self.ui.tk_button_m8b95daa.config(text="开始")

    def update_progress(self, value):
        """更新进度条"""
        self.ui.tk_progressbar_m8b910ks['value'] = value
        self.ui.update_idletasks()

    def select_output_path(self):
        """选择保存路径"""
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx")]
        )
        if path:
            self.ui.tk_input_m8b95r63.delete(0, 'end')
            self.ui.tk_input_m8b95r63.insert(0, path)

    def export_result(self):
        """导出结果"""
        if not self.service.has_result():
            messagebox.showwarning("警告", "没有可导出的结果")
            return

        path = self.ui.tk_input_m8b95r63.get()
        try:
            self.service.export_result(path)
            messagebox.showinfo("成功", f"文件已保存到：{path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{str(e)}")

    def add_student(self):
        """添加学生"""
        name = self.ui.tk_input_m8b9sdst.get().strip()
        if not name:
            messagebox.showwarning("提示", "请输入学生姓名")
            return

        try:
            student_type = int(self.ui.tk_text_m8b9mw1x.get("1.0", "end").strip())
            if student_type not in (1, 0, -1, -2):
                raise ValueError
        except:
            messagebox.showerror("错误", "无效的学生类型（必须为1/0/-1/-2）")
            return

        try:
            self.service.add_student(name, student_type)
            self.update_student_table(self.service.get_students())
            self.log(f"已添加学生：{name}")
        except Exception as e:
            messagebox.showerror("错误", f"添加失败：{str(e)}")

    def log(self, message):
        """记录日志"""
        self.ui.tk_text_m8b930ud.insert('end', f"{time.strftime('%H:%M:%S')} {message}\n")
        self.ui.tk_text_m8b930ud.see('end')
        self.ui.update_idletasks()