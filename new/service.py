# service.py
import json
import os
import random
import pandas as pd
from threading import Event


class ClassroomService:
    def __init__(self):
        self.students = []
        self.current_class = None
        self.current_result = None
        self.stop_event = Event()

    # 班级管理
    def get_available_classes(self):
        """获取所有班级"""
        return [f[:-5] for f in os.listdir('.') if f.endswith('.json')]

    def load_class(self, class_name):
        """加载班级数据"""
        try:
            with open(f"{class_name}.json", 'r') as f:
                self.students = json.load(f)
                self.current_class = class_name
            return self.students
        except Exception as e:
            raise ServiceError(f"加载班级失败: {str(e)}")

    def save_class(self):
        """保存当前班级"""
        if not self.current_class:
            raise ServiceError("未选择班级")

        try:
            with open(f"{self.current_class}.json", 'w') as f:
                json.dump(self.students, f, indent=2)
        except Exception as e:
            raise ServiceError(f"保存失败: {str(e)}")

    # 学生管理
    def add_student(self, name, student_type):
        """添加学生"""
        if any(s['name'] == name for s in self.students):
            raise ServiceError("学生已存在")
        self.students.append({'name': name, 'type': student_type})

    def get_students(self):
        """获取当前学生列表"""
        return self.students.copy()

    def has_students(self):
        """是否有学生数据"""
        return len(self.students) > 0

    # 核心算法
    def arrange(self, seed, thread_num, progress_callback, log_callback):
        """执行排列算法"""
        self.stop_event.clear()
        try:
            random.seed(seed)
            students = self.students.copy()
            n = len(students)
            total = n ** n

            # 模拟进度更新
            for i in range(100):
                if self.stop_event.is_set():
                    return None
                progress = (i + 1) * 100 // 100
                progress_callback(progress)
                log_callback(f"正在尝试第{i + 1}种排列...")
                time.sleep(0.1)  # 模拟计算耗时

            # 返回模拟结果
            return {'seed': seed, 'layout': [[students[0]]]}

        except Exception as e:
            raise ServiceError(f"排列失败: {str(e)}")

    def stop(self):
        """停止计算"""
        self.stop_event.set()

    # 结果处理
    def has_result(self):
        return self.current_result is not None

    def export_result(self, path):
        """导出结果到Excel"""
        if not self.current_result:
            raise ServiceError("没有可导出的结果")

        try:
            data = []
            for row in self.current_result['layout']:
                data.append([f"{s['name']}({s['type']})" for s in row])

            df = pd.DataFrame(data)
            df.to_excel(path, index=False, header=False)
        except Exception as e:
            raise ServiceError(f"导出失败: {str(e)}")


class ServiceError(Exception):
    pass