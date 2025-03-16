import json
import os
import random
import threading
import time
from tqdm import tqdm
import pandas as pd


class ClassroomArranger:
    def __init__(self, student_file="students.json"):
        self.student_file = student_file
        self.students = self.load_or_create_students()
        self.n = len(self.students)
        self.rows, self.cols = self.calculate_layout()
        self.found_event = threading.Event()
        self.lock = threading.Lock()
        self.result = None
        self.seed = None
        self.max_attempts = self.n ** self.n
        self.attempts = 0
        self.progress = None

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
        print(f"\n{'=' * 30}")
        print(f" {self.student_file} 文件不存在")
        print(f"{'=' * 30}")
        print("请按以下格式输入学生信息：")

        while True:
            name = input("\n学生姓名（直接回车结束输入）: ").strip()
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
        print(f"\n✅ 学生信息已保存至 {self.student_file}")

    def calculate_layout(self):
        """计算教室行列布局"""
        sqrt = int(self.n ** 0.5)
        for i in range(sqrt, 0, -1):
            if self.n % i == 0:
                return i, self.n // i
        return 1, self.n

    def check_partial(self, grid, row, col):
        """逐步检查当前座位有效性"""
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
        """生成并验证排列"""
        random.seed(seed)
        shuffled = random.sample(self.students, self.n)

        grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        idx = 0

        for i in range(self.rows):
            for j in range(self.cols):
                if idx >= self.n:
                    return grid

                grid[i][j] = shuffled[idx]
                if not self.check_partial(grid, i, j):
                    return None
                idx += 1
        return grid

    def worker(self):
        """工作线程"""
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
        """主运行方法"""
        print(f"\n教室布局: {self.rows}行×{self.cols}列")
        print(f"学生总数: {self.n}")
        print(f"最大尝试次数: {self.max_attempts}\n")

        self.progress = tqdm(total=self.max_attempts,
                             desc="正在搜索有效排列",
                             bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [用时:{elapsed}<剩余:{remaining}]")

        threads = []
        for _ in range(thread_num):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            threads.append(t)
            t.start()

        # 进度更新
        last_attempts = 0
        while not self.found_event.is_set() and self.attempts < self.max_attempts:
            time.sleep(0.3)
            with self.lock:
                current = self.attempts
            self.progress.update(current - last_attempts)
            last_attempts = current

        self.found_event.set()
        for t in threads:
            t.join(timeout=0.1)
        self.progress.close()

    def export_excel(self, filename="座位表.xlsx"):
        """导出Excel文件"""
        if not self.result:
            raise ValueError("没有找到有效排列")

        data = []
        for row in self.result:
            data_row = []
            for student in row:
                if student:
                    data_row.append(f"{student['name']} ({student['type']})")
                else:
                    data_row.append("空座位")
            data.append(data_row)

        df = pd.DataFrame(data, columns=[f"第{i + 1}列" for i in range(self.cols)])
        df.index = [f"第{i + 1}行" for i in range(self.rows)]
        df.to_excel(filename, engine='openpyxl')
        print(f"\n✅ 座位表已保存到 {os.path.abspath(filename)}")


if __name__ == "__main__":
    try:
        arranger = ClassroomArranger()
        arranger.find_arrangement(thread_num=4)

        if arranger.result:
            arranger.export_excel()
            print(f"成功种子号: {arranger.seed}")
        else:
            print("\n⚠️ 未找到有效排列，建议调整学生类型后重试")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")