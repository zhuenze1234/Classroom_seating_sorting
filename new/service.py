# service.py
import json
import os
import random
import pandas as pd
from threading import Event


class ClassroomService:
    def __init__(self):
        self.students = []
        self.current_result = None
        self.stop_event = Event()

    def add_student(self, name, student_type):
        """添加学生"""
        if any(s['name'] == name for s in self.students):
            raise ValueError("学生姓名重复")
        if student_type not in (1, 0, -1, -2):
            raise ValueError("无效的学生类型")
        self.students.append({'name': name, 'type': student_type})

    def arrange(self, seed, thread_num, progress_callback, log_callback):
        """执行排列算法"""
        self.stop_event.clear()
        try:
            n = len(self.students)
            total = n ** n

            # 模拟计算过程
            for i in range(100):
                if self.stop_event.is_set():
                    return None

                # 更新进度（实际算法需替换此处）
                progress = (i + 1)
                progress_callback(progress)

                # 记录日志
                log_callback(f"尝试第{i + 1}种排列...")
                time.sleep(0.1)

            # 返回模拟结果
            return {'seed': seed, 'layout': [self.students]}

        except Exception as e:
            raise RuntimeError(f"排列失败: {str(e)}")
        finally:
            self.stop_event.set()


class ServiceError(Exception):
    pass