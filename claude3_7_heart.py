import pygame
import math
import random
import sys

# 初始化pygame
pygame.init()

# 屏幕设置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("跳动的爱心")

# 颜色
BACKGROUND = (0, 0, 0)  # 黑色背景
PINK = (255, 105, 180)  # 粉红色
RED = (255, 0, 0)  # 红色
WHITE = (255, 255, 255)  # 白色

# 爱心形状参数
HEART_SIZE = 8  # 心形基础大小
HEART_X = WIDTH // 2  # 心形X坐标（屏幕中心）
HEART_Y = HEIGHT // 2  # 心形Y坐标（屏幕中心）


# 粒子类
class Particle:
    def __init__(self, x, y, color=(255, 105, 180)):
        self.x = x
        self.y = y
        self.original_x = x
        self.original_y = y
        self.size = random.uniform(2, 4)
        self.color = color
        self.speed_x = random.uniform(-0.5, 0.5)
        self.speed_y = random.uniform(-0.5, 0.5)
        self.life = 255  # 粒子透明度/生命值
        self.max_distance = random.uniform(5, 15)  # 粒子最大漂移距离

    def update(self, heartbeat_intensity):
        # 计算与原始位置的距离
        dx = self.x - self.original_x
        dy = self.y - self.original_y
        distance = math.sqrt(dx * dx + dy * dy)

        # 如果距离太远，增加向原点的引力
        if distance > self.max_distance:
            self.speed_x -= dx * 0.01
            self.speed_y -= dy * 0.01

        # 更新位置
        self.x += self.speed_x
        self.y += self.speed_y

        # 添加随机抖动
        self.x += random.uniform(-0.5, 0.5)
        self.y += random.uniform(-0.5, 0.5)

        # 心跳时的位置调整 (向外扩散)
        if heartbeat_intensity > 0:
            direction_x = self.original_x - HEART_X
            direction_y = self.original_y - HEART_Y
            length = math.sqrt(direction_x ** 2 + direction_y ** 2)
            if length > 0:
                self.x += direction_x / length * heartbeat_intensity
                self.y += direction_y / length * heartbeat_intensity

    def draw(self, surface, alpha=255):
        # 计算当前颜色（带透明度）
        color = (*self.color, alpha)
        # 绘制粒子
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.size))


# 生成心形点集
def generate_heart_points(num_points, size, x, y):
    points = []
    for i in range(num_points):
        # 参数t从0到2π
        t = 2 * math.pi * i / num_points

        # 参数方程（更明确的心形）
        x_point = 16 * math.sin(t) ** 3
        y_point = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)

        # 缩放和定位
        x_point = x_point * size + x
        y_point = -y_point * size + y  # 反转Y轴使心形正立

        points.append((x_point, y_point))

    return points


# 主函数
def main():
    clock = pygame.time.Clock()

    # 创建表面用于绘制（支持透明度）
    particle_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    # 生成心形轮廓点
    heart_points = generate_heart_points(200, HEART_SIZE, HEART_X, HEART_Y)

    # 从轮廓点创建粒子
    particles = []
    for point in heart_points:
        # 为每个轮廓点创建多个粒子
        for _ in range(2):  # 每个点2个粒子
            # 在点附近随机位置生成粒子
            offset_x = random.uniform(-2, 2)
            offset_y = random.uniform(-2, 2)
            # 随机颜色（粉红色到红色的渐变）
            r = random.randint(220, 255)
            g = random.randint(20, 105)
            b = random.randint(100, 180)
            particle = Particle(point[0] + offset_x, point[1] + offset_y, (r, g, b))
            particles.append(particle)

    # 在内部填充更多粒子
    for _ in range(500):
        t = random.uniform(0, 2 * math.pi)
        # 参数方程
        r = random.uniform(0, 0.8)  # 随机半径系数（确保在内部）
        x_point = 16 * math.sin(t) ** 3
        y_point = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)

        # 缩放和定位
        x_point = x_point * HEART_SIZE * r + HEART_X
        y_point = -y_point * HEART_SIZE * r + HEART_Y

        # 随机颜色（内部粒子更亮）
        r = random.randint(230, 255)
        g = random.randint(40, 120)
        b = random.randint(120, 200)

        particle = Particle(x_point, y_point, (r, g, b))
        particles.append(particle)

    # 心跳参数
    heartbeat = 0
    heartbeat_speed = 0.05
    max_heartbeat_intensity = 5

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # 更新心跳
        heartbeat += heartbeat_speed
        heartbeat_intensity = max_heartbeat_intensity * abs(math.sin(heartbeat)) ** 2

        # 调整心跳模式（收缩和扩张的不对称模式，更像真实心脏）
        if math.sin(heartbeat) > 0 and math.sin(heartbeat - heartbeat_speed) <= 0:
            # 心脏收缩开始 - 快速收缩
            heartbeat_speed = 0.1
        elif math.sin(heartbeat) < 0 and math.sin(heartbeat - heartbeat_speed) >= 0:
            # 心脏扩张开始 - 慢速扩张
            heartbeat_speed = 0.03

        # 清屏
        screen.fill(BACKGROUND)
        particle_surface.fill((0, 0, 0, 0))  # 透明背景

        # 更新和绘制所有粒子
        for particle in particles:
            particle.update(heartbeat_intensity)
            # 根据心跳状态调整粒子大小和透明度
            size_mult = 1 + 0.3 * heartbeat_intensity / max_heartbeat_intensity
            alpha = 200 + 55 * heartbeat_intensity / max_heartbeat_intensity
            # 绘制到透明表面
            particle.draw(particle_surface, min(255, alpha))

        # 添加发光效果
        if heartbeat_intensity > max_heartbeat_intensity * 0.7:
            # 在高强度心跳时添加额外的发光效果
            glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            glow_intensity = int(80 * (heartbeat_intensity / max_heartbeat_intensity))
            glow_color = (255, 100, 150, glow_intensity)
            glow_radius = int(100 + 30 * heartbeat_intensity / max_heartbeat_intensity)
            pygame.draw.circle(glow_surf, glow_color, (HEART_X, HEART_Y), glow_radius)
            screen.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_ADD)

        # 将粒子表面绘制到屏幕上
        screen.blit(particle_surface, (0, 0))

        # 显示帧率（调试用）
        # fps = str(int(clock.get_fps()))
        # font = pygame.font.SysFont('Arial', 20)
        # fps_text = font.render(fps, True, WHITE)
        # screen.blit(fps_text, (10, 10))

        # 更新屏幕
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()