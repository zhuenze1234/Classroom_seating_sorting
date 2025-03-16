import json
import os
import random
import threading
import time
from tqdm import tqdm
import pandas as pd


class ClassroomArranger:
    def __init__(self, student_file):
        self.student_file = student_file
        self.students = self.load_or_create_students()  # 这里调用了方法
        self.n = len(self.students)
        self.rows, self.cols = self.calculate_layout()
        self.found_event = threading.Event()
        self.lock = threading.Lock()
        self.result = None
        self.seed = None
        self.max_attempts = self.n ** self.n
        self.attempts = 0
        self.progress = None

    # 新增的完整方法实现
    def load_or_create_students(self):
        """加载或创建学生数据文件"""
        if not os.path.exists(self.student_file):
            self.create_student_file()

        with open(self.student_file, 'r') as f:
            students = json.load(f)
            if not students:
                raise ValueError("学生列表不能为空")
            return students

    def create_student_file(self):
        """交互式创建学生文件"""
        students = []
        print(f"{self.student_file} 文件不存在，请手动输入学生信息：")
        while True:
            name = input("学生姓名（直接回车结束输入）: ").strip()
            if not name:
                if len(students) == 0:
                    print("至少需要输入一个学生！")
                    continue
                break

            while True:
                try:
                    student_type = int(input(f"{name}的类型 (1/0/-1/-2): "))
                    if student_type not in (1, 0, -1, -2):
                        raise ValueError
                    break
                except:
                    print("无效类型！请输入1, 0, -1 或 -2")

            students.append({"name": name, "type": student_type})

        with open(self.student_file, 'w') as f:
            json.dump(students, f, indent=2)
        print(f"学生信息已保存至 {self.student_file}")

    # 其他方法保持不变...
    # [保持原有 calculate_layout、check_partial 等方法不变]
    # ...

    def check_partial(self, grid, row, col):
        """逐步检查当前座位是否有效"""
        student = grid[row][col]
        if not student:
            return True

        # 检查好学生管理
        if student['type'] < 0:
            has_good = False
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    x, y = row + dx, col + dy
                    if 0 <= x < self.rows and 0 <= y < self.cols:
                        if grid[x][y] and grid[x][y]['type'] == 1:
                            has_good = True
                            break
                if has_good:
                    break
            if not has_good:
                return False

        # 检查坏学生相邻规则
        if student['type'] == -1:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                x, y = row + dx, col + dy
                if 0 <= x < self.rows and 0 <= y < self.cols:
                    if grid[x][y] and grid[x][y]['type'] < 0:
                        return False
        elif student['type'] == -2:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    x, y = row + dx, col + dy
                    if 0 <= x < self.rows and 0 <= y < self.cols:
                        if grid[x][y] and grid[x][y]['type'] < 0:
                            return False
        return True

    def generate_and_validate(self, seed):
        """生成并逐步验证排列"""
        random.seed(seed)
        shuffled = random.sample(self.students, self.n)

        grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        idx = 0

        for i in range(self.rows):
            for j in range(self.cols):
                if idx >= self.n:
                    return grid  # 允许有空座位

                grid[i][j] = shuffled[idx]
                if not self.check_partial(grid, i, j):
                    return None  # 立即终止无效排列
                idx += 1
        return grid

    def worker(self):
        """工作线程函数（改进版）"""
        while not self.found_event.is_set():
            with self.lock:
                if self.attempts >= self.max_attempts:
                    return
                seed = self.attempts
                self.attempts += 1

            grid = self.generate_and_validate(seed)
            if grid:
                with self.lock:
                    if not self.found_event.is_set():
                        self.result = grid
                        self.seed = seed
                        self.found_event.set()

    def find_arrangement(self, thread_num=4):
        """带进度条的主算法"""
        self.progress = tqdm(total=self.max_attempts, desc="正在搜索排列")

        threads = []
        for _ in range(thread_num):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            threads.append(t)
            t.start()

        # 进度更新线程
        def update_progress():
            while not self.found_event.is_set() and self.attempts < self.max_attempts:
                self.progress.n = self.attempts
                self.progress.refresh()
                time.sleep(0.1)

        progress_thread = threading.Thread(target=update_progress)
        progress_thread.start()

        self.found_event.wait()
        self.progress.close()

        # 清理线程
        for t in threads:
            t.join(timeout=0.1)
        progress_thread.join()
    def calculate_layout(self):
        sqrt = int(self.n ** 0.5)
        for i in range(sqrt, 0, -1):
            if self.n % i == 0:
                return i, self.n // i
        return 1, self.n

    def is_valid(self, grid):
        for i in range(self.rows):
            for j in range(self.cols):
                student = grid[i][j]
                if not student:
                    continue

                # 检查好学生是否能管理坏学生
                if student['type'] < 0:
                    has_good = False
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            x, y = i + dx, j + dy
                            if 0 <= x < self.rows and 0 <= y < self.cols:
                                neighbor = grid[x][y]
                                if neighbor and neighbor['type'] == 1:
                                    has_good = True
                                    break
                        if has_good:
                            break
                    if not has_good:
                        return False

                # 检查坏学生相邻规则
                if student['type'] == -1:
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        x, y = i + dx, j + dy
                        if 0 <= x < self.rows and 0 <= y < self.cols:
                            neighbor = grid[x][y]
                            if neighbor and neighbor['type'] < 0:
                                return False
                elif student['type'] == -2:
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            if dx == 0 and dy == 0:
                                continue
                            x, y = i + dx, j + dy
                            if 0 <= x < self.rows and 0 <= y < self.cols:
                                neighbor = grid[x][y]
                                if neighbor and neighbor['type'] < 0:
                                    return False
        return True

    def generate_arrangement(self, seed):
        random.seed(seed)
        shuffled = random.sample(self.students, self.n)
        return [shuffled[i * self.cols: (i + 1) * self.cols] for i in range(self.rows)]
        # 等待第一个完成的结果
        self.found_event.wait()

        # 终止其他线程
        for t in threads:
            t.join(timeout=0.1)

    def export_excel(self, filename):
        if not self.result:
            raise ValueError("没有找到有效排列")

        df = pd.DataFrame(
            [[f"{cell['name']}({cell['type']})" if cell else ""
              for cell in row]
             for row in self.result],
            columns=[f"座位{i + 1}" for i in range(self.cols)]
        )
        df.to_excel(filename, index=False)
        print(f"结果已导出到 {filename}")






if __name__ == "__main__":
    try:
        arranger = ClassroomArranger("students.json")
        print(f"共{arranger.n}名学生，最大尝试次数：{arranger.max_attempts}")
        arranger.find_arrangement()

        if arranger.result:
            arranger.export_excel("arrangement.xlsx")
            print(f"成功找到有效排列，种子号：{arranger.seed}")
        else:
            print(f"在{arranger.max_attempts}次尝试后未找到有效排列")
    except Exception as e:
        print(f"发生错误：{str(e)}")