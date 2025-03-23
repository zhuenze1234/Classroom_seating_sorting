# service.py
import math
import random
import json
import numpy as np
from threading import Event, Lock
from itertools import permutations, islice
from queue import Queue

class ClassroomService:
    def __init__(self):
        self.students = []
        self.current_result = None
        self.stop_event = Event()
        self.best_solution = None
        self.solution_lock = Lock()  # 修正：导入Lock类

    def calculate_layout_size(self, student_count):
        """智能计算最小合适布局尺寸"""
        if student_count == 0:
            return 0, 0

        # 寻找最接近正方形的布局
        min_size = math.ceil(math.sqrt(student_count))

        # 优先选择接近黄金分割的比例
        candidates = []
        for w in range(min_size, min_size + 3):
            for h in range(min_size, min_size + 3):
                if w * h >= student_count:
                    ratio = max(w / h, h / w)
                    candidates.append((ratio, w, h))

        # 选择最接近1:1的比例
        candidates.sort()
        return candidates[0][1], candidates[0][2]
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

    def _convert_to_seating_chart(self, layout):
        """转换布局为行列结构"""
        chart = []
        for row in layout:
            chart_row = []
            for seat in row:
                chart_row.append({
                    'name': seat['name'] if seat else "空",
                    'type': seat['type'] if seat else None
                })
            chart.append(chart_row)
        return chart

    # 核心排列算法
    def arrange(self, seed, thread_num, progress_callback, log_callback):
        """优化后的穷举算法"""
        self.stop_event.clear()
        try:
            students = self.students.copy()
            n = len(students)
            if n == 0:
                raise ValueError("没有可排列的学生数据")

            # 计算布局尺寸
            size = math.ceil(math.sqrt(n))
            total_seats = size * size
            required_empty = total_seats - n

            # 生成所有可能的空座位组合
            all_positions = list(range(total_seats))
            empty_positions = set()

            # 创建任务队列
            task_queue = Queue()
            batch_size = 1000

            # 生成排列批次
            def generate_permutations():
                while not self.stop_event.is_set():
                    # 随机生成空座位组合
                    empty = set(random.sample(all_positions, required_empty))
                    if empty not in empty_positions:
                        empty_positions.add(frozenset(empty))
                        yield empty

                    # 随机打乱学生顺序
                    shuffled = random.sample(students, n)
                    yield shuffled

            # 创建工作线程
            workers = []
            for _ in range(thread_num):
                t = threading.Thread(
                    target=self._arrangement_worker,
                    args=(generate_permutations(), size, progress_callback),
                    daemon=True
                )
                workers.append(t)
                t.start()

            # 等待结果
            while not self.stop_event.is_set():
                if self.best_solution:
                    self.stop_event.set()
                    break
                time.sleep(0.1)

            # 清理线程
            for t in workers:
                t.join()

            return self.best_solution

        except Exception as e:
            raise ServiceError(f"排列失败: {str(e)}")
        finally:
            self.stop_event.set()

    def _arrangement_worker(self, permutation_generator, size, progress_callback):
        """工作线程处理函数"""
        try:
            for attempt, candidates in enumerate(permutation_generator):
                if self.stop_event.is_set():
                    return

                # 生成布局
                if isinstance(candidates, set):  # 处理空座位
                    layout = self._create_layout_with_empty(size, candidates)
                else:  # 处理学生排列
                    layout = self._arrange_students(candidates, size)

                # 验证布局
                if self._validate_full_layout(layout):
                    with self.solution_lock:
                        if not self.best_solution:
                            self.best_solution = {
                                'seed': random.randint(0, 2 ** 32),
                                'layout': self._convert_to_seating_chart(layout)
                            }
                            self.stop_event.set()
                    return

                # 更新进度
                if attempt % 100 == 0:
                    progress_callback(min(attempt / 1000 * 100, 99))

        except Exception as e:
            print(f"工作线程错误: {str(e)}")

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

    def get_layout_preview(self, layout):
        """生成表格预览数据"""
        preview = []
        for row_idx, row in enumerate(layout):
            preview_row = {f"列{i + 1}": seat['name'] if seat else "" for i, seat in enumerate(row)}
            preview_row["行"] = f"第{row_idx + 1}排"
            preview.append(preview_row)
        return preview

    def _create_layout_with_empty(self, size, empty_positions):
        """创建带空座位的布局"""
        layout = np.full((size, size), None, dtype=object)
        for pos in empty_positions:
            row = pos // size
            col = pos % size
            layout[row][col] = {'name': '空座位', 'type': None}
        return layout

    def _arrange_students(self, students, size):
        """将学生填入布局"""
        layout = np.full((size, size), None, dtype=object)
        student_iter = iter(students)
        for i in range(size):
            for j in range(size):
                if layout[i][j] is None:
                    try:
                        layout[i][j] = next(student_iter)
                    except StopIteration:
                        pass
        return layout

    def _validate_full_layout(self, layout):
        """完整验证布局"""
        size = layout.shape[0]
        for i in range(size):
            for j in range(size):
                student = layout[i][j]
                if student and student['type'] is not None:
                    if not self._validate_student(layout, i, j):
                        return False
        return True

    def _validate_student(self, layout, row, col):
        """验证单个学生位置"""
        student = layout[row][col]
        if student['type'] < 0:
            # 检查附近是否有同类型学生
            neighbors = self._get_neighbors(layout, row, col,
                                            distance=2 if student['type'] == -2 else 1)
            if any(n and n['type'] == student['type'] for n in neighbors):
                return False

            # 检查是否有好学生管理
            if student['type'] == -2:
                has_good = any(n and n['type'] == 1 for n in neighbors)
                if not has_good:
                    return False
        return True

    def _get_neighbors(self, layout, row, col, distance=1):
        """获取周围邻居（优化版）"""
        size = layout.shape[0]
        neighbors = []
        for dx in range(-distance, distance + 1):
            for dy in range(-distance, distance + 1):
                if dx == 0 and dy == 0:
                    continue
                x, y = row + dx, col + dy
                if 0 <= x < size and 0 <= y < size:
                    neighbors.append(layout[x][y])
        return neighbors

    def get_max_seed(self):
        """安全计算排列数"""
        n = len(self.students)
        try:
            return math.factorial(n)
        except OverflowError:
            return None

class ServiceError(Exception):
    """自定义服务异常"""
    pass
