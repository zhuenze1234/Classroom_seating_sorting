# service.py
import json
import random
import numpy as np
from threading import Event
from itertools import permutations

class ClassroomService:
    def __init__(self):
        self.students = []
        self.current_result = None
        self.stop_event = Event()

    # 学生管理方法
    def add_student(self, name, student_type):
        """添加学生验证（增强版）"""
        if not name:
            raise ValueError("姓名不能为空")
        if any(s['name'].lower() == name.lower() for s in self.students):
            raise ValueError("学生姓名不能重复")
        if student_type not in (1, 0, -1, -2):
            raise ValueError("无效的学生类型")
        self.students.append({'name': name, 'type': student_type})

    def load_from_json(self, filepath):
        """JSON加载（增强验证）"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("JSON根元素必须是数组")

            required_fields = {'name', 'type'}
            for index, item in enumerate(data):
                if not isinstance(item, dict):
                    raise ValueError(f"第{index + 1}条数据不是对象")
                if not required_fields.issubset(item.keys()):
                    raise ValueError(f"第{index + 1}条数据缺少必要字段")
                if not isinstance(item['name'], str) or not item['name'].strip():
                    raise ValueError(f"第{index + 1}条姓名无效")
                if item['type'] not in (1, 0, -1, -2):
                    raise ValueError(f"第{index + 1}条类型无效")

            self.students = data
        except json.JSONDecodeError as e:
            raise ValueError(f"无效的JSON格式：{str(e)}")
        except Exception as e:
            raise ValueError(f"加载失败：{str(e)}")

    # 核心排列算法
    def arrange(self, seed, thread_num, progress_callback, log_callback):
        """优化后的排列算法"""
        self.stop_event.clear()
        try:
            if not self.students:
                raise ValueError("没有可排列的学生数据")

            # 初始化随机种子
            random.seed(seed)
            students = self.students.copy()
            total_steps = 0

            # 学生分类
            good_students = [s for s in students if s['type'] == 1]
            normal_students = [s for s in students if s['type'] == 0]
            bad_students = [s for s in students if s['type'] in (-1, -2)]

            # 动态计算布局尺寸
            total = len(students)
            size = int(total ** 0.5) + 1
            if size * size < total:
                size += 1

            log_callback(f"创建{size}x{size}的座位布局")
            layout = np.full((size, size), None, dtype=object)

            # 先放置问题学生
            for student in [s for s in bad_students if s['type'] == -2]:
                pos = self._find_valid_position(layout, size, student)
                layout[pos] = student
                total_steps +=1
                progress_callback(total_steps/(size*size)*100)

            for student in [s for s in bad_students if s['type'] == -1]:
                pos = self._find_valid_position(layout, size, student)
                layout[pos] = student
                total_steps +=1
                progress_callback(total_steps/(size*size)*100)

            # 放置好学生
            for student in good_students:
                pos = self._place_good_student(layout, size)
                layout[pos] = student
                total_steps +=1
                progress_callback(total_steps/(size*size)*100)

            # 填充剩余学生
            remaining = [s for s in students if s not in layout.flatten()]
            for i in range(size):
                for j in range(size):
                    if self.stop_event.is_set():
                        return None
                    if layout[i,j] is None and remaining:
                        layout[i,j] = remaining.pop()
                        total_steps +=1
                        progress_callback(total_steps/(size*size)*100)

            return {'seed': seed, 'layout': layout.tolist()}

        except Exception as e:
            raise RuntimeError(f"排列失败: {str(e)}")
        finally:
            self.stop_event.set()

    # 辅助方法
    def _find_valid_position(self, layout, size, student):
        """为问题学生寻找合适位置"""
        for _ in range(100):
            i, j = random.randint(0,size-1), random.randint(0,size-1)
            if layout[i,j] is None and self._validate_position(layout, size, i, j, student):
                return (i,j)
        raise RuntimeError("无法找到合适位置")

    def _validate_position(self, layout, size, i, j, student):
        """验证位置有效性"""
        if student['type'] == -1:
            neighbors = self._get_neighbors(layout, size, i, j, 1)
            return all(n['type'] == 0 if n else True for n in neighbors)
        elif student['type'] == -2:
            neighbors = self._get_neighbors(layout, size, i, j, 2)
            return (any(n['type'] == 1 for n in neighbors if n) and
                    all(n['type'] == 0 if n else True for n in neighbors))
        return True

    def _place_good_student(self, layout, size):
        """放置好学生"""
        for _ in range(100):
            i, j = random.randint(0,size-1), random.randint(0,size-1)
            if layout[i,j] is None:
                neighbors = self._get_neighbors(layout, size, i, j, 1)
                if any(n and n['type'] in (-1,-2) for n in neighbors):
                    return (i,j)
        return self._find_valid_position(layout, size, {'type': 1})

    def _get_neighbors(self, layout, size, i, j, distance):
        """获取周围邻居"""
        neighbors = []
        for dx in (-distance, 0, distance):
            for dy in (-distance, 0, distance):
                x, y = i+dx, j+dy
                if 0 <= x < size and 0 <= y < size:
                    neighbors.append(layout[x,y])
        return neighbors

class ServiceError(Exception):
    """自定义服务异常"""
    pass
