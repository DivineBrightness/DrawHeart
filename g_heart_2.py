import pygame
import math
import random
from pygame.locals import *


class Vector3:
    """三维向量类"""

    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def __mul__(self, scalar):
        """标量乘法"""
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __add__(self, other):
        """向量加法"""
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def dot(self, other):
        """点积"""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def normalize(self):
        """归一化"""
        length = math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
        return Vector3(self.x / length, self.y / length, self.z / length)

    def as_int(self):
        """转换为整数元组"""
        return (
            min(255, max(0, int(self.x))),
            min(255, max(0, int(self.y))),
            min(255, max(0, int(self.z)))
        )

    @staticmethod
    def from_color(color):
        """从颜色元组创建向量"""
        return Vector3(color[0], color[1], color[2])


# 初始化Pygame
pygame.init()

# 颜色定义
DEEP_PINK = (255, 20, 147)
HOT_PINK = (255, 105, 180)
SPEC_COLOR = (255, 255, 200)
AMBIENT_COLOR = (255, 192, 203, 50)


class StereoHeart:
    def __init__(self, width=800, height=600):
        self.screen = pygame.display.set_mode((width, height), RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.center = (width // 2, height // 2)

        # 3D参数
        self.heart_scale = 0.7
        self.depth = 3.0
        self.rotation = 0
        self.light_dir = Vector3(1, -1, 0.5).normalize()

        # 动画参数
        self.beat_phase = 0
        self.particles = []
        self.heart_points = self.generate_3d_heart()

        # 光照参数
        self.ambient_strength = 0.3
        self.specular_power = 20

    def generate_3d_heart(self, samples=300):
        """生成3D心形顶点"""
        points = []
        for t in (i * 2 * math.pi / samples for i in range(samples)):
            x = 15 * (math.sin(t) ** 3)
            y = 12.5 * math.cos(t) - 4.5 * math.cos(2 * t) - 2 * math.cos(3 * t) - 0.5 * math.cos(4 * t)

            # 创建三个深度层
            for z in [-self.depth, 0, self.depth]:
                scale = 1 + abs(z) / self.depth * 0.1
                normal = Vector3(
                    math.sin(t) * scale,
                    math.cos(t) * scale,
                    z / self.depth
                ).normalize()
                points.append({
                    'pos': Vector3(x * scale, y * scale, z),
                    'normal': normal
                })
        return points

    def project_point(self, point):
        """3D到2D投影"""
        rot = self.rotation * math.pi / 180
        x = point.x * math.cos(rot) - point.z * math.sin(rot)
        z = point.x * math.sin(rot) + point.z * math.cos(rot)
        y = point.y

        scale = 10 * self.heart_scale * (1 + 0.1 * math.sin(self.beat_phase))
        return (int(self.center[0] + x * scale),
                int(self.center[1] - y * scale * 0.8 + z * scale * 0.3))

    def calculate_lighting(self, normal):
        """3D光照计算"""
        diff = max(0, normal.dot(self.light_dir))
        spec = diff ** self.specular_power
        return min(1.0, self.ambient_strength + diff + spec)

    def update_animation(self):
        """更新动画状态"""
        self.beat_phase += 0.05
        self.rotation += 0.7

        # 更新光源方向
        time = pygame.time.get_ticks() / 1000
        self.light_dir = Vector3(
            math.cos(time),
            math.sin(time * 0.8),
            math.sin(time * 0.6)
        ).normalize()

        # 生成粒子
        if len(self.particles) < 200:
            self.particles.append({
                'pos': Vector3(
                    self.center[0] + random.uniform(-50, 50),
                    self.center[1] + random.uniform(-40, 40),
                    random.uniform(-self.depth, self.depth)
                ),
                'vel': Vector3(
                    random.uniform(-1, 1),
                    random.uniform(-1, 1),
                    random.uniform(-0.5, 0.5)
                ),
                'life': 1.0
            })

        # 更新粒子状态
        for p in self.particles:
            p['pos'] = p['pos'] + p['vel'] * 0.3
            p['vel'] = p['vel'] * 0.95
            p['life'] -= 0.01
        self.particles = [p for p in self.particles if p['life'] > 0]

    def draw_scene(self):
        """绘制3D场景"""
        self.screen.fill((30, 30, 50))

        # 环境光晕
        glow = pygame.Surface((400, 400), pygame.SRCALPHA)
        pygame.draw.circle(glow, AMBIENT_COLOR, (200, 200),
                           180 + 30 * math.sin(self.beat_phase))
        self.screen.blit(glow, (self.center[0] - 200, self.center[1] - 200))

        # 深度排序
        sorted_objects = sorted(
            self.particles + self.heart_points,
            key=lambda x: x['pos'].z if isinstance(x, dict) else x['pos'].z,
            reverse=True
        )

        for obj in sorted_objects:
            if 'vel' in obj:  # 绘制粒子
                pos = self.project_point(obj['pos'])
                alpha = int(200 * obj['life'])
                size = max(1, int(3 - abs(obj['pos'].z) / self.depth * 2))
                color = (255, 255 - size * 40, 255 - size * 60, alpha)
                pygame.draw.circle(self.screen, color, pos, size)
            else:  # 绘制心形
                pos = self.project_point(obj['pos'])
                intensity = self.calculate_lighting(obj['normal'])

                # 计算基础颜色
                base_color = Vector3.from_color(DEEP_PINK)
                target_color = Vector3.from_color(HOT_PINK)
                t = (obj['pos'].z + self.depth) / (2 * self.depth)
                base_color = Vector3(
                    base_color.x + (target_color.x - base_color.x) * t,
                    base_color.y + (target_color.y - base_color.y) * t,
                    base_color.z + (target_color.z - base_color.z) * t
                )

                # 计算高光颜色
                spec_strength = intensity ** 5
                spec_color = Vector3.from_color(SPEC_COLOR) * spec_strength

                # 混合颜色
                final_color = (base_color * intensity + spec_color).as_int()

                # 绘制
                radius = max(2, int(4 - abs(obj['pos'].z) / self.depth * 2))
                pygame.draw.circle(self.screen, final_color, pos, radius)

                # 添加高光点
                if intensity > 0.7:
                    highlight_pos = (
                        pos[0] + obj['normal'].x * 5,
                        pos[1] + obj['normal'].y * 5
                    )
                    pygame.draw.circle(self.screen, (255, 255, 255, 150), highlight_pos, 1)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == VIDEORESIZE:
                    self.center = (event.w // 2, event.h // 2)

            self.update_animation()
            self.draw_scene()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    StereoHeart().run()
    pygame.quit()