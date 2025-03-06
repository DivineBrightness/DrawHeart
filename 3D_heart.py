import pygame
import math
import random
from pygame.locals import *


class Vector3:
    """三维向量类"""

    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalize(self):
        mag = self.magnitude()
        return Vector3(self.x / mag, self.y / mag, self.z / mag) if mag != 0 else self

    def rotate(self, axis, angle):
        """绕任意轴旋转"""
        cos = math.cos(angle)
        sin = math.sin(angle)
        t = 1 - cos
        x, y, z = axis.normalize().x, axis.normalize().y, axis.normalize().z

        return Vector3(
            (t * x * x + cos) * self.x + (t * x * y - z * sin) * self.y + (t * x * z + y * sin) * self.z,
            (t * x * y + z * sin) * self.x + (t * y * y + cos) * self.y + (t * y * z - x * sin) * self.z,
            (t * x * z - y * sin) * self.x + (t * y * z + x * sin) * self.y + (t * z * z + cos) * self.z
        )


class ParticleHeart:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height), RESIZABLE)
        self.clock = pygame.time.Clock()
        self.width, self.height = width, height
        self.running = True

        # 颜色定义
        self.colors = [
            (255, 51, 153),  # 深粉
            (255, 105, 180),  # 热粉
            (255, 182, 193)  # 浅粉
        ]

        # 3D参数
        self.camera_pos = Vector3(0, -200, 200)  # 摄像机位置
        self.light_dir = Vector3(1, 1, -1).normalize()

        # 心形参数
        self.particles = []
        self.init_particles(3000)  # 粒子数量

        # 动画参数
        self.angle = 0
        self.beat_phase = 0
        self.rotation_speed = 0.02
        self.beat_speed = 2.5
        self.beat_strength = 0.15

    def init_particles(self, count):
        """初始化3D心形粒子"""
        for _ in range(count):
            u = random.uniform(0, 2 * math.pi)
            v = random.uniform(-math.pi / 2, math.pi / 2)

            # 心形参数方程（3D）
            x = 16 * (math.sin(u) ** 3) * (1 + 0.2 * math.cos(v))
            y = (13 * math.cos(u) - 5 * math.cos(2 * u) - 2 * math.cos(3 * u) - math.cos(4 * u)) * (
                        1 + 0.2 * math.sin(v))
            z = 8 * math.sin(v)

            pos = Vector3(x, y, z)
            velocity = Vector3(0, 0, 0)

            self.particles.append({
                'pos': pos,
                'origin': pos,  # 存储原始位置
                'velocity': velocity,
                'color': random.choice(self.colors)
            })

    def project(self, point):
        """3D投影到2D屏幕（简单透视投影）"""
        fov = 256  # 视野系数
        scale = self.height / (self.height + point.z)
        x = int(self.width / 2 + (point.x - self.camera_pos.x) * fov * scale)
        y = int(self.height / 2 + (point.y - self.camera_pos.y) * fov * scale)
        return x, y

    def calculate_lighting(self, normal):
        """计算光照强度"""
        intensity = max(0, normal.dot(self.light_dir)) * 0.8 + 0.2
        return min(max(intensity, 0.3), 1.0)

    def update_particles(self):
        """更新粒子物理状态"""
        self.angle += self.rotation_speed
        self.beat_phase += self.beat_speed / 60

        # 计算心跳变形
        beat = (math.sin(self.beat_phase) * 0.5 + 0.5) * self.beat_strength + 1
        beat_vec = Vector3(beat, beat, beat * 0.8)

        for p in self.particles:
            # 基础动画：旋转 + 心跳
            rotated = p['origin'].rotate(Vector3(0, 1, 0), self.angle)
            rotated = rotated.rotate(Vector3(1, 0, 0), math.radians(20))

            # 应用心跳变形
            target_pos = Vector3(
                rotated.x * beat_vec.x,
                rotated.y * beat_vec.y,
                rotated.z * beat_vec.z
            )

            # 物理模拟（弹簧效果）
            force = (target_pos - p['pos']) * 0.1
            p['velocity'] = p['velocity'] * 0.9 + force
            p['pos'] = p['pos'] + p['velocity']

            # 计算法线（用于光照）
            dx = math.sin(p['pos'].x * 0.5) * 0.3
            dy = math.cos(p['pos'].y * 0.5) * 0.3
            normal = Vector3(dx, dy, 1).normalize()

            # 更新颜色
            light = self.calculate_lighting(normal)
            p['display_color'] = tuple(min(255, int(c * light)) for c in p['color'])

    def draw(self):
        """绘制粒子系统"""
        self.screen.fill((25, 25, 35))  # 深空背景

        # 根据深度排序粒子（从远到近）
        sorted_particles = sorted(self.particles,
                                  key=lambda p: p['pos'].z,
                                  reverse=True)

        for p in sorted_particles:
            x, y = self.project(p['pos'])
            if 0 <= x < self.width and 0 <= y < self.height:
                size = max(1, int(3 - p['pos'].z * 0.05))
                pygame.draw.circle(self.screen, p['display_color'], (x, y), size)

                # 添加高光
                if random.random() < 0.1:
                    pygame.draw.circle(self.screen,
                                       (255, 255, 255, 100),
                                       (x, y), size + 1, 1)

        # 绘制光源方向指示
        light_x = int(self.width / 2 + self.light_dir.x * 50)
        light_y = int(self.height / 2 + self.light_dir.y * 50)
        pygame.draw.line(self.screen, (255, 255, 0),
                         (self.width // 2, self.height // 2),
                         (light_x, light_y), 2)

    def run(self):
        """主循环"""
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_UP:
                        self.beat_speed += 0.2
                    elif event.key == K_DOWN:
                        self.beat_speed -= 0.2
                elif event.type == VIDEORESIZE:
                    self.width, self.height = event.size
                    self.screen = pygame.display.set_mode((self.width, self.height), RESIZABLE)

            self.update_particles()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    ParticleHeart().run()