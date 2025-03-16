# control.py
import threading
import time
from tkinter import messagebox, filedialog
from service import ClassroomService



class Controller:
    def __init__(self):
        self.service = ClassroomService()
        self.running = False
        self.ui = None

    def init(self, ui):
        """初始化控制器"""
        self.ui = ui
        self._bind_events()
        self._init_components()
        self._update_seed_limit()
        self.load_student_table()

    # control.py
    # 在Controller类中添加以下方法
    def import_json(self):
        """导入JSON学生数据"""
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON文件", "*.json")]
        )
        if not filepath:
            return

        try:
            # 调用服务层方法加载数据
            self.service.load_from_json(filepath)
            self.load_student_table()
            self._update_seed_limit()
            self.log(f"成功导入文件：{filepath}")
            messagebox.showinfo("导入成功", "学生数据已加载")
        except Exception as e:
            messagebox.showerror("导入失败", str(e))
            self.log(f"导入错误：{str(e)}")

    # service.py
    # 在ClassroomService类中添加以下方法
    def load_from_json(self, filepath):
        """从JSON文件加载学生数据"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                students = json.load(f)

            # 验证数据格式
            if not isinstance(students, list):
                raise ValueError("数据格式错误：应为学生列表")

            for s in students:
                if 'name' not in s or 'type' not in s:
                    raise ValueError("数据格式错误：缺少name或type字段")
                if s['type'] not in (1, 0, -1, -2):
                    raise ValueError(f"无效的学生类型：{s['type']}")

            self.students = students
        except json.JSONDecodeError:
            raise ValueError("文件格式错误：不是有效的JSON")
        except Exception as e:
            raise ServiceError(f"加载失败：{str(e)}")

    def _bind_events(self):
        """绑定所有事件"""
        events = [
            (self.ui.tk_button_m8b8z6uo, self.generate_random_seed),
            (self.ui.tk_button_m8b9519y, self._set_thread_count),
            (self.ui.tk_button_m8b95daa, self.toggle_arrangement),
            (self.ui.tk_button_m8b96nxu, self.select_output_path),
            (self.ui.tk_button_m8b9721p, self.export_result),
            (self.ui.tk_button_m8b9siwe, self.add_student),
            (self.ui.tk_button_m8betf3s, self.import_json)
        ]
        for widget, callback in events:
            widget.config(command=callback)

    def _init_components(self):
        """初始化组件状态"""
        # 线程数设置
        self.ui.tk_scale_m8b91zcg.config(from_=1, to=8)
        self.ui.tk_scale_m8b91zcg.set(4)
        self.ui.tk_input_m8b925pn.insert(0, "4")

        # 默认值设置
        self.ui.tk_input_m8b8y7zs.insert(0, "0")
        self.ui.tk_input_m8b95r63.insert(0, "座位表.xlsx")

        # 表格配置
        self.ui.tk_table_m8bg960c.heading("ID", text="ID")
        self.ui.tk_table_m8bg960c.heading("姓名", text="姓名")
        self.ui.tk_table_m8bg960c.heading("等级", text="等级")

    def load_student_table(self):
        """加载学生表格数据"""
        self.ui.tk_table_m8bg960c.delete(*self.ui.tk_table_m8bg960c.get_children())
        for idx, student in enumerate(self.service.students):
            self.ui.tk_table_m8bg960c.insert("", "end",
                                             values=(idx + 1, student['name'], self._type_to_text(student['type'])))

    def _type_to_text(self, t):
        """转换类型为文字说明"""
        return {
            1: "好学生", 0: "普通学生",
            -1: "说话学生", -2: "严重说话"
        }.get(t, "未知")

    def _update_seed_limit(self):
        """更新种子输入验证"""
        max_seed = max(len(self.service.students), 1)
        self.ui.tk_input_m8b8y7zs.config(validate="key",
                                         validatecommand=(self.ui.register(self._validate_seed), '%P', max_seed))

    def _validate_seed(self, value, max_seed):
        """种子验证逻辑"""
        try:
            return 0 <= int(value) <= max_seed if value else True
        except ValueError:
            return False

    def generate_random_seed(self):
        """生成随机种子"""
        if not self.service.students:
            messagebox.showwarning("提示", "请先添加学生")
            return

        max_seed = len(self.service.students)
        seed = random.randint(0, max_seed)
        self.ui.tk_input_m8b8y7zs.delete(0, 'end')
        self.ui.tk_input_m8b8y7zs.insert(0, str(seed))

    def _set_thread_count(self):
        """设置线程数"""
        try:
            count = int(self.ui.tk_input_m8b925pn.get())
            if 1 <= count <= 8:
                self.ui.tk_scale_m8b91zcg.set(count)
                self.log(f"线程数已设置为：{count}")
            else:
                messagebox.showwarning("提示", "线程数范围1-8")
        except ValueError:
            messagebox.showerror("错误", "请输入有效数字")

    def toggle_arrangement(self):
        """切换排列状态"""
        if self.running:
            self.stop_arrangement()
        else:
            self.start_arrangement()

    def start_arrangement(self):
        """开始排列算法"""
        # 验证参数
        try:
            params = self._validate_params()
        except ValueError as e:
            messagebox.showerror("参数错误", str(e))
            return

        # 初始化状态
        self.running = True
        self.ui.tk_button_m8b95daa.config(text="停止")
        self.ui.tk_progressbar_m8b910ks['value'] = 0
        self.log("开始计算座位排列...")

        # 启动线程
        threading.Thread(
            target=self._run_arrangement,
            args=(params['seed'], params['thread_num']),
            daemon=True
        ).start()

    def _validate_params(self):
        """验证输入参数"""
        params = {}

        # 验证学生数据
        if not self.service.students:
            raise ValueError("请先添加学生数据")

        # 验证种子
        try:
            params['seed'] = int(self.ui.tk_input_m8b8y7zs.get())
            max_seed = len(self.service.students)
            if not (0 <= params['seed'] <= max_seed):
                raise ValueError
        except:
            raise ValueError(f"种子必须为0-{max_seed}之间的整数")

        # 验证线程数
        try:
            params['thread_num'] = int(self.ui.tk_input_m8b925pn.get())
            if not (1 <= params['thread_num'] <= 8):
                raise ValueError
        except:
            raise ValueError("线程数必须为1-8之间的整数")

        return params

    def _run_arrangement(self, seed, thread_num):
        """运行排列算法"""
        try:
            result = self.service.arrange(
                seed=seed,
                thread_num=thread_num,
                progress_callback=self._update_progress,
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

    def _update_progress(self, value):
        """更新进度条"""
        self.ui.tk_progressbar_m8b910ks['value'] = value
        self.ui.update_idletasks()

    def log(self, message):
        """记录日志"""
        self.ui.tk_text_m8b930ud.insert('end', f"{time.strftime('%H:%M:%S')} {message}\n")
        self.ui.tk_text_m8b930ud.see('end')

    # 其他方法（导出、导入等）保持核心逻辑不变
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