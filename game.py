import math

import pygame
import random
import numpy as np
import heapq

# 初始化pygame
pygame.init()

# 定义窗口尺寸
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.init()
pygame.display.set_caption("Ball Avoidance Game-1024客户运营部技术节")

# 定义颜色
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
# 小球半径
BALL_RADIUS = 20


# 定义小球类
class Ball:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = BALL_RADIUS

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        # 确保小球不越界
        self.x = max(self.radius, min(self.x, WIDTH - self.radius))
        self.y = max(self.radius, min(self.y, HEIGHT - self.radius))

    def draw(self, surface):
        pygame.draw.circle(surface, GREEN, (self.x, self.y), self.radius)

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"


# 定义障碍物类
class Obstacle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = 0
        self.square_length = BALL_RADIUS * 2
        self.speed = 2

    def fall(self):
        self.y += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, RED, (self.x, self.y,
                                        self.square_length, self.square_length))

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"


'''
    此处代码可以自行修改实现，返回合适的小球位置(左，上，右，下)即可。
    左：（1,0,0,0）
    上：（0,1,0,0）
    右：（0,0,1,0）
    下：（0,0,0,1）
    不动:(0,0,0,0)
'''
def ball_move_direction(ball, obstacles):
    # 最近的可被20整除的整数
    def closest_multiple_of_20(px):
        # 计算离 px 最近的整数，可以正数和负数方向均考虑
        lower_multiple = (px // 20) * 20
        upper_multiple = lower_multiple + 20

        # 判定哪个距离 px 更近
        if px - lower_multiple < upper_multiple - px:
            return lower_multiple
        else:
            return upper_multiple

    # 第一步，找到最安全的区域
    def find_best_position():
        # 定义一个大的安全距离常量
        SAFE_DISTANCE = 100

        best_point = None
        max_distance = -1  # 用于记录最大安全距离

        # 遍历可能的位置
        for px in range(BALL_RADIUS, WIDTH - BALL_RADIUS, 20):
            for py in range(60, HEIGHT - BALL_RADIUS, 20):
                # 计算该点到所有障碍物的最小距离
                min_distance_to_obstacle = float('inf')
                for obstacle in obstacles:
                    if obstacle.y > HEIGHT:
                        continue
                    cx, cy = obstacle.x + BALL_RADIUS, obstacle.y + BALL_RADIUS
                    distance = math.sqrt((px - cx) ** 2 + (py - cy) ** 2)
                    if distance < min_distance_to_obstacle:
                        min_distance_to_obstacle = distance

                # 判断该点是否是更安全的点
                if min_distance_to_obstacle > max_distance and min_distance_to_obstacle > SAFE_DISTANCE:
                    max_distance = min_distance_to_obstacle

                    best_point = (closest_multiple_of_20(px), closest_multiple_of_20(py))
        pygame.draw.circle(window, (0, 0, 255), (best_point[0], best_point[1]), ball.radius)
        return best_point

    def is_colliding_after_fall(x, y, obstacle):
        # 计算小木块的边界
        left = obstacle.x
        right = obstacle.x + obstacle.square_length
        top = obstacle.y + obstacle.speed
        bottom = obstacle.y + obstacle.speed + obstacle.square_length

        # 计算小球的边界
        ball_radius = ball.radius
        ball_left = x - ball_radius
        ball_right = x + ball_radius
        ball_top = y - ball_radius
        ball_bottom = y + ball_radius

        # 检查小球是否与小木块重叠
        return (ball_right >= left and
                ball_left <= right and
                ball_bottom >= top and
                ball_top <= bottom)

    # Check collision in the primary direction
    def will_collide(primary_direction):
        future_x, future_y = ball.x, ball.y

        if primary_direction == "left":
            future_x -= BALL_RADIUS
        elif primary_direction == "right":
            future_x += BALL_RADIUS
        elif primary_direction == "up":
            future_y -= BALL_RADIUS
        elif primary_direction == "down":
            future_y += BALL_RADIUS

        # Check future position with each obstacle
        for obstacle in obstacles:
            if obstacle.y > HEIGHT:
                continue
            if is_colliding_after_fall(future_x, future_y, obstacle):
                return True

        return False

    # 找到当前点前往best_point的路径，确定下一步移动方向
    # breadth first search。广度优先搜索的寻路算法，关键是queue，把每个点和该点的整个路径存下来，最终找到终点。
    # 广度优先搜索可以找到最小路径，比深度优先要好，但是计算速度往往比深度优先慢。
    # 当前实现不具备启发性（heuristic），可以借助欧式方向（坐标）和曼哈顿方向（网格）提供启发式的方向帮助
    def way_to_best_point():
        directions = ['left', 'up', 'right', 'down']
        queue = [(ball.x, ball.y, [])]  # 队列存储位置和路径
        visited = set((ball.x, ball.y))  # 记录访问过的位置

        while queue:
            x, y, path = queue.pop(0)

            # 如果已经到达best_point，则返回路径
            if (x, y) == best_point:
                return path

            # 尝试每一种方向
            for direction in directions:
                if direction == 'left':
                    new_x = x - BALL_RADIUS
                    new_y = y
                elif direction == 'up':
                    new_x = x
                    new_y = y - BALL_RADIUS
                elif direction == 'right':
                    new_x = x + BALL_RADIUS
                    new_y = y
                elif direction == 'down':
                    new_x = x
                    new_y = y + BALL_RADIUS

                # 边界检测
                new_x = max(BALL_RADIUS, min(new_x, WIDTH - BALL_RADIUS))
                new_y = max(BALL_RADIUS, min(new_y, HEIGHT - BALL_RADIUS))

                # 如果没有访问过且不与障碍物碰撞，记录新的位置和路径
                new_position = (new_x, new_y)
                if new_position not in visited:
                    temp_ball = Ball()
                    temp_ball.x = new_x
                    temp_ball.y = new_y

                    if not any(is_colliding(temp_ball, ob) for ob in obstacles):
                        if not any(is_colliding_after_fall(new_x, new_y, obs) for obs in obstacles):
                            visited.add(new_position)
                            queue.append((new_x, new_y, path + [new_position]))

        # 如果没有任何路径可以到达best_point，返回空列表
        return []

    best_point = find_best_position()
    paths = way_to_best_point()
    for p in paths:
        pygame.draw.circle(window, (255, 0, 255), (p[0], p[1]), ball.radius / 20)

    pos_flags=[0,0,0,0]
    if paths:
        pos = paths[0]
        if ball.x < pos[0]:
            pos_flags = [0, 0, 1, 0]
        elif ball.x > pos[0]:
            pos_flags = [1, 0, 0, 0]
        elif ball.y < pos[1]:
            pos_flags = [0, 0, 0, 1]
        elif ball.y > pos[1]:
            pos_flags = [0, 1, 0, 0]

    return pos_flags


# 检测碰撞，考虑球的半径
def is_colliding(ball, obstacle):
    # 计算小木块的边界
    left = obstacle.x
    right = obstacle.x + obstacle.square_length
    top = obstacle.y
    bottom = obstacle.y + obstacle.square_length

    # 计算小球的边界
    ball_radius = ball.radius
    ball_left = ball.x - ball_radius
    ball_right = ball.x + ball_radius
    ball_top = ball.y - ball_radius
    ball_bottom = ball.y + ball_radius

    # 检查小球是否与小木块重叠
    return (ball_right >= left and
            ball_left <= right and
            ball_bottom >= top and
            ball_top <= bottom)


# 游戏循环渲染，一个线程重绘小球和障碍物
def main():
    clock = pygame.time.Clock()
    ball = Ball()
    obstacles = []
    running = True

    total_run_nums = 0
    while running:
        # 刷新频率不需要修改
        clock.tick(50)
        # 1秒一个障碍物，增加障碍物
        if total_run_nums % 10 == 0:  # 降低障碍物的生成频率
            obstacles.append(Obstacle())

        total_run_nums += 1
        window.fill(WHITE)

        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 移动小球，这里可以替换决策代码，基于障碍物和位置数据进行决策判断
        (left, up, right, down) = ball_move_direction(ball, obstacles)
        dx, dy = (0, 0)
        if left == 1:
            dx -= BALL_RADIUS
        elif up == 1:
            dy -= BALL_RADIUS
        elif right == 1:
            dx += BALL_RADIUS
        elif down == 1:
            dy += BALL_RADIUS
        else:
            None

        ball.move(dx, dy)

        # 移动和绘制障碍物
        for obstacle in obstacles:
            if obstacle.y > HEIGHT:
                continue
            obstacle.fall()
            obstacle.draw(window)

            # 检测碰撞，球的圆心坐标在小木块内，包括边沿接触
            if is_colliding(ball, obstacle):
                print(ball, obstacle)
                print(f"Game Over! Your score is: {len(obstacles)}")
                running = False

        # 绘制得分到屏幕上
        # 定义文本
        if running:
            text = 'Your score: %d' % len(obstacles)
        else:
            text = 'GameOver,Your score: %d' % len(obstacles)

        font = pygame.font.SysFont("SimHei", 30)
        # 准备渲染文本
        surface = font.render(text, True, (255, 108, 10))
        window.blit(surface, (20, 20))
        ball.draw(window)
        pygame.display.flip()

    # 处理事件
    done = False
    while not done:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            done = True
    # 退出PyGame
    pygame.quit()


if __name__ == "__main__":
    main()
