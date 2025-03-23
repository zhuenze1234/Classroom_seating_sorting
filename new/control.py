# control.py
import json
import math
import os
import random
import threading
import time
from pathlib import Path
from tkinter import messagebox, filedialog

import pandas as pd

from service import ClassroomService


class Controller:
    def __init__(self):
        self.service = ClassroomService()
        self.running = False
        self.ui = None
        self.config_file = "app_config.json"
        self.load_config()
        self.last_opened_dir = str(Path.home())
        self._load_config()

    def init(self, ui):
        """初始化控制器"""
        self.ui = ui
        self._bind_events()
        self._init_components()
        self._update_seed_limit()
        self.load_student_table()

    # 事件绑定
    def _bind_events(self):
        event_map = [
            (self.ui.tk_button_m8b8z6uo, self.generate_random_seed),
            (self.ui.tk_button_m8b9519y, self._set_thread_count),
            (self.ui.tk_button_m8b95daa, self.toggle_arrangement),
            (self.ui.tk_button_m8b96nxu, self.select_output_path),
            (self.ui.tk_button_m8b9721p, self.export_result),
            (self.ui.tk_button_m8betf3s, self.add_student),
            (self.ui.tk_button_m8bgba2z, self.import_json),
            (self.ui.tk_button_save, self.save_students)
        ]
        for widget, callback in event_map:
            widget.config(command=callback)

    # 组件初始化
    def _init_components(self):
        self.ui.tk_scale_m8b91zcg.config(from_=1, to=8)
        self.ui.tk_scale_m8b91zcg.set(4)
        self.ui.tk_input_m8b925pn.delete(0, 'end')
        self.ui.tk_input_m8b925pn.insert(0, "4")
        self.ui.tk_input_m8b8y7zs.insert(0, "0")
        self.ui.tk_input_m8b95r63.insert(0, "座位表.xlsx")

    # 学生表格管理
    def load_student_table(self):
        self.ui.tk_table_m8bg960c.delete(*self.ui.tk_table_m8bg960c.get_children())
        for idx, student in enumerate(self.service.students):
            self.ui.tk_table_m8bg960c.insert("", "end", values=(
                idx + 1,
                student['name'],
                self._type_to_text(student['type'])
            ))

    def _load_config(self):
        """加载应用程序配置"""
        try:
            if Path(self.CONFIG_FILE).exists():
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.last_opened_dir = config.get('last_opened_dir', str(Path.home()))
        except Exception as e:
            print(f"加载配置失败: {str(e)}")

        def _save_config(self):
            """保存应用程序配置"""
            config = {
                'last_opened_dir': self.last_opened_dir
            }
            try:
                with open(self.CONFIG_FILE, 'w') as f:
                    json.dump(config, f)
            except Exception as e:
                print(f"保存配置失败: {str(e)}")
    def _type_to_text(self, t):
        type_map = {
            1: "好学生", 0: "普通学生",
            -1: "说话学生", -2: "严重说话"
        }
        return type_map.get(t, "未知")

    # 种子管理
    def _update_seed_limit(self):
        """更新种子范围为n!"""
        n = len(self.service.students)
        try:
            max_seed = math.factorial(n) if n > 0 else 1
            self.ui.tk_input_m8b8y7zs.config(
                validate="key",
                validatecommand=(self.ui.register(self._validate_seed), '%P', max_seed)
            )
        except OverflowError:
            # 处理超过计算范围的情况
            self.log("警告：学生数量过多，已启用随机模式")
            self.ui.tk_input_m8b8y7zs.config(validate='none')

    def _validate_seed(self, value, max_seed):
        """验证种子输入"""
        try:
            max_seed = int(max_seed)
            if value == "": return True
            input_val = int(value)
            return 0 <= input_val < max_seed
        except:
            return False

    def generate_random_seed(self):
        """生成随机种子（基于n!）"""
        n = len(self.service.students)
        if n == 0:
            messagebox.showwarning("提示", "请先添加学生")
            return

        try:
            max_seed = math.factorial(n)
            seed = random.randint(0, max_seed - 1)
            self.ui.tk_input_m8b8y7zs.delete(0, 'end')
            self.ui.tk_input_m8b8y7zs.insert(0, str(seed))
        except OverflowError:
            self.log("学生数量过多，使用系统随机种子")
            seed = random.getrandbits(128)
            self.ui.tk_input_m8b8y7zs.delete(0, 'end')
            self.ui.tk_input_m8b8y7zs.insert(0, str(seed))

    # 核心业务逻辑
    def toggle_arrangement(self):
        if self.running:
            self.stop_arrangement()
        else:
            self.start_arrangement()

    def start_arrangement(self):

        """添加大数验证"""
        n = len(self.service.students)
        if n > 10:
            if not messagebox.askyesno("确认",
                                       "10人以上排列可能需要较长时间，是否继续？"):
                return

        try:
            max_seed = self.service.get_max_seed()
            if max_seed is None:
                messagebox.showwarning("警告",
                                       "学生数量过多，将使用系统随机种子")
            params = self._validate_params()
            self.running = True
            self.ui.tk_button_m8b95daa.config(text="停止")
            self.ui.tk_progressbar_m8b910ks['value'] = 0
            self.log("开始计算座位排列...")

            threading.Thread(
                target=self._run_arrangement,
                args=(params['seed'], params['thread_num']),
                daemon=True
            ).start()
        except ValueError as e:
            messagebox.showerror("参数错误", str(e))

    def _validate_params(self):
        global max_seed
        params = {}
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
                self._show_result(result)
            else:
                self.log("排列被中止")
        except Exception as e:
            self.log(f"发生错误：{str(e)}")
        finally:
            self.running = False
            self.ui.tk_button_m8b95daa.config(text="开始")
            self._update_progress(100)

    def _show_result(self, result):
        """优化结果显示"""
        layout = result['layout']

        # 清空原有数据
        self.ui.tk_table_m8awzxkt.delete(*self.ui.tk_table_m8awzxkt.get_children())

        # 动态生成列
        columns = [f"列{i + 1}" for i in range(len(layout[0]))] + ["行"]
        self.ui.tk_table_m8awzxkt["columns"] = columns

        # 设置列格式
        for col in columns:
            self.ui.tk_table_m8awzxkt.heading(col, text=col, anchor='center')
            self.ui.tk_table_m8awzxkt.column(col, width=80, anchor='center')

        # 填充数据
        for row_idx, row in enumerate(layout):
            values = []
            for seat in row:
                if seat and seat['name'] != '空座位':
                    values.append(f"{seat['name']}({self._type_to_text(seat['type'])})")
                else:
                    values.append("")
            values.append(f"第{row_idx + 1}行")
            self.ui.tk_table_m8awzxkt.insert("", "end", values=values)

    # 其他功能
    def import_json(self):
        """改进后的文件选择对话框"""
        filepath = filedialog.askopenfilename(
            initialdir=self.last_opened_dir,
            filetypes=[("JSON文件", "*.json")],
            title="选择学生数据文件"
        )
        if filepath:
            self.last_opened_dir = str(Path(filepath).parent)
            self._save_config()
            try:
                self.service.load_from_json(filepath)
                self.load_student_table()
                self._update_seed_limit()
                self.log(f"成功导入：{filepath}")
                messagebox.showinfo("导入成功", "学生数据已加载")
            except Exception as e:
                messagebox.showerror("导入失败", str(e))
                self.log(f"导入错误：{str(e)}")

    def add_student(self):
        name = self.ui.tk_input_m8b9sdst.get().strip()
        student_type = self.ui.tk_input_m8betb1b.get().strip()

        error_msg = []
        if not name:
            error_msg.append("姓名不能为空")
        try:
            student_type = int(student_type)
            if student_type not in (1, 0, -1, -2):
                error_msg.append("类型必须为1/0/-1/-2")
        except ValueError:
            error_msg.append("类型必须为数字")

        if error_msg:
            messagebox.showerror("输入错误", "\n".join(error_msg))
            return

        try:
            self.service.add_student(name, student_type)
            self.ui.tk_input_m8b9sdst.delete(0, 'end')
            self.ui.tk_input_m8betb1b.delete(0, 'end')
            self.load_student_table()
            self._update_seed_limit()
            self.log(f"已添加学生：{name}（类型：{student_type}）")
        except ValueError as e:
            messagebox.showerror("错误", str(e))

    def _set_thread_count(self):
        """同步滑块和输入框的线程数"""
        try:
            count = int(self.ui.tk_input_m8b925pn.get())
            if 1 <= count <= 8:
                self.ui.tk_scale_m8b91zcg.set(count)
                self.log(f"线程数已设置为：{count}")
            else:
                messagebox.showwarning("提示", "线程数范围1-8")
        except ValueError:
            messagebox.showerror("错误", "请输入有效数字")

    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.last_opened_file = config.get('last_file')
                self.auto_save = config.get('auto_save', True)
        except:
            self.last_opened_file = None
            self.auto_save = True

    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w') as f:
            json.dump({
                'last_file': self.last_opened_file,
                'auto_save': self.auto_save
            }, f)


            # ...原有导入逻辑...

    def auto_save_students(self):
        """自动保存学生数据"""
        if self.auto_save and self.last_opened_file:
            try:
                with open(self.last_opened_file, 'w') as f:
                    json.dump(self.service.students, f, ensure_ascii=False, indent=2)
            except Exception as e:
                self.log(f"自动保存失败：{str(e)}")


    # 工具方法
    def _update_progress(self, value):
        self.ui.tk_progressbar_m8b910ks['value'] = value
        self.ui.update_idletasks()

    def log(self, message):
        self.ui.tk_text_m8b930ud.insert('end', f"{time.strftime('%H:%M:%S')} {message}\n")
        self.ui.tk_text_m8b930ud.see('end')

    def select_output_path(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx")]
        )
        if path:
            self.ui.tk_input_m8b95r63.delete(0, 'end')
            self.ui.tk_input_m8b95r63.insert(0, path)

    def export_result(self):
        """改进的Excel导出"""
        if not self.service.current_result:
            messagebox.showwarning("警告", "没有可导出的结果")
            return

        path = self.ui.tk_input_m8b95r63.get()
        try:
            # 获取布局数据
            layout = self.service.current_result['layout']

            # 创建DataFrame
            data = []
            max_cols = max(len(row) for row in layout)
            columns = [f"列{i + 1}" for i in range(max_cols)]

            for row_idx, row in enumerate(layout, 1):
                row_data = {"行": f"第{row_idx}排"}
                for col_idx, seat in enumerate(row, 1):
                    if seat and seat['name'] != '空座位':
                        row_data[f"列{col_idx}"] = f"{seat['name']}({self._type_to_text(seat['type'])})"
                    else:
                        row_data[f"列{col_idx}"] = ""
                data.append(row_data)

            df = pd.DataFrame(data).fillna("")
            df.set_index("行", inplace=True)

            # 导出Excel
            df.to_excel(path, engine='openpyxl')

            messagebox.showinfo("成功", f"文件已保存到：{path}")
            self.log(f"成功导出结果到：{path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{str(e)}")
            self.log(f"导出错误：{str(e)}")

    def _load_config(self):
        """加载用户配置"""
        self.config_path = "app_config.json"
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {"last_open_path": "", "last_save_path": ""}

    def _save_config(self):
        """保存用户配置"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)

    def export_student_data(self):
        """导出学生信息"""
        filepath = filedialog.asksaveasfilename(
            filetypes=[("JSON文件", "*.json")],
            title="保存学生数据",
            initialdir=self.config.get("last_save_path", "")
        )
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.service.students, f, ensure_ascii=False)
                self.config["last_save_path"] = os.path.dirname(filepath)
                self._save_config()
                messagebox.showinfo("保存成功", "学生数据已保存")
            except Exception as e:
                messagebox.showerror("保存失败", str(e))

    def show_layout_preview(self, layout_data):
        """在表格中显示布局结果"""
        # 清空表格
        for item in self.ui.tk_table_m8awzxkt.get_children():
            self.ui.tk_table_m8awzxkt.delete(item)

        # 设置列头
        columns = [f"列 {i + 1}" for i in range(len(layout_data[0]))]
        self.ui.tk_table_m8awzxkt["columns"] = columns
        self.ui.tk_table_m8awzxkt.heading("#0", text="行号", anchor='center')

        for col in columns:
            self.ui.tk_table_m8awzxkt.heading(col, text=col, anchor='center')
            self.ui.tk_table_m8awzxkt.column(col, width=80, anchor='center')

        # 填充数据
        for row_idx, row in enumerate(layout_data, 1):
            values = [f"{s['name']}({s['type']})" if s else "" for s in row]
            self.ui.tk_table_m8awzxkt.insert("", "end",
                                             text=f"行 {row_idx}",
                                             values=values)

    def save_students(self):
        """保存学生数据"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if filepath:
            try:
                data = [dict(name=s['name'], type=s['type']) for s in self.service.students]
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("保存成功", "学生数据已保存")
                self.log(f"数据已保存至：{filepath}")
            except Exception as e:
                messagebox.showerror("保存失败", str(e))
                self.log(f"保存错误：{str(e)}")