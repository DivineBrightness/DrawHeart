import pygame
import math
import random
from pygame.locals import *

# 初始化Pygame
pygame.init()

# 定义颜色常量
DARK_PINK = (255, 51, 153)
LIGHT_PINK = (255, 182, 193)
WHITE = (255, 255, 255)
SHADOW_COLOR = (200, 0, 100)


class HeartAnimation:
    def __init__(self, screen_width=800, screen_height=600):
        # 初始化显示设置
        self.screen = pygame.display.set_mode((screen_width, screen_height), RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2

        # 可调节参数
        self.base_scale = 1.0  # 减小基础尺寸
        self.animation_speed = 1.0
        self.particle_count = 50
        self.beat_frequency = 1.2

        # 初始化缩放比例
        self.current_scale = self.base_scale

        # 初始化粒子系统
        self.particles = []

        # 优化后的心形参数方程（更圆润）
        self.heart_points = []
        t = 0
        while t < 2 * math.pi:
            # 调整后的心形方程
            x = 15 * (math.sin(t) ** 3)
            y = 12.5 * math.cos(t) - 4.5 * math.cos(2 * t) - 2 * math.cos(3 * t) - 0.5 * math.cos(4 * t)
            self.heart_points.append((x, y))
            t += 0.02  # 增加采样密度

    def calculate_scale(self):
        """计算动态缩放比例"""
        time = pygame.time.get_ticks() / 1000
        beat = math.sin(time * math.pi * self.beat_frequency) * 0.08  # 减小跳动幅度
        tremor = random.uniform(-0.008, 0.008)  # 减小颤动幅度
        return self.base_scale * (1 + beat + tremor)

    def generate_particles(self):
        """生成粒子效果"""
        if len(self.particles) < self.particle_count:
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(8, 15) * self.current_scale  # 调整粒子生成范围
            x = self.center_x + radius * math.cos(angle)
            y = self.center_y + radius * math.sin(angle)
            self.particles.append({
                'pos': [x, y],
                'speed': [random.uniform(-0.8, 0.8), random.uniform(-1.5, 0)],
                'radius': random.uniform(1, 2.5),  # 减小粒子尺寸
                'life': 1.0
            })

    def update_particles(self):
        """更新粒子状态"""
        for p in self.particles:
            p['pos'][0] += p['speed'][0] * self.animation_speed
            p['pos'][1] += p['speed'][1] * self.animation_speed
            p['life'] -= 0.015 * self.animation_speed  # 延长生命周期
            p['speed'][1] += 0.08  # 减小重力效果
        self.particles = [p for p in self.particles if p['life'] > 0]

    def calculate_color(self, y_pos):
        """颜色渐变计算"""
        progress = (y_pos - (self.center_y - 40 * self.current_scale)) / (80 * self.current_scale)
        progress = max(0, min(1, progress))
        r = DARK_PINK[0] + (LIGHT_PINK[0] - DARK_PINK[0]) * progress
        g = DARK_PINK[1] + (LIGHT_PINK[1] - DARK_PINK[1]) * progress
        b = DARK_PINK[2] + (LIGHT_PINK[2] - DARK_PINK[2]) * progress
        return (int(r), int(g), int(b))

    def draw_heart(self):
        """绘制优化后的心形"""
        # 生成基础形状坐标
        base_points = [
            (
                x * 8 * self.current_scale,  # 减小放大倍数
                y * 8 * self.current_scale
            ) for x, y in self.heart_points
        ]

        # 主心形坐标
        main_points = [
            (self.center_x + x, self.center_y - y) for x, y in base_points
        ]

        # 阴影层坐标（向右下方偏移）
        shadow_points = [
            (self.center_x + x + 4 * self.current_scale,
             self.center_y - y + 4 * self.current_scale)
            for x, y in base_points
        ]

        # 高光层坐标（向左上方偏移并缩小）
        highlight_points = [
            (self.center_x + x * 0.85 - 2 * self.current_scale,  # 修正高光位置
             self.center_y - y * 0.85 - 2 * self.current_scale)
            for x, y in base_points
        ]

        # 绘制阴影
        pygame.draw.polygon(self.screen, SHADOW_COLOR, shadow_points)

        # 绘制主心形（渐变填充）
        for point in main_points:
            color = self.calculate_color(point[1])
            pygame.draw.circle(self.screen, color, (int(point[0]), int(point[1])),
                               int(3.5 * self.current_scale))  # 调整绘制尺寸

        # 绘制高光边框
        pygame.draw.polygon(self.screen, WHITE, highlight_points, 3)

    def handle_resize(self, event):
        """窗口大小调整"""
        self.center_x = event.w // 2
        self.center_y = event.h // 2

    def run(self):
        while self.running:
            self.screen.fill((30, 30, 30))  # 深灰色背景

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == VIDEORESIZE:
                    self.handle_resize(event)

            self.current_scale = self.calculate_scale()

            self.generate_particles()
            self.update_particles()

            # 绘制粒子（半透明效果）
            for p in self.particles:
                alpha = int(200 * p['life'])  # 降低最大透明度
                surface = pygame.Surface((50, 50), pygame.SRCALPHA)
                pygame.draw.circle(surface, (255, 255, 255, alpha),
                                   (25, 25), int(p['radius']))
                self.screen.blit(surface, (int(p['pos'][0] - p['radius']),
                                           int(p['pos'][1] - p['radius'])))

            self.draw_heart()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    animation = HeartAnimation()
    animation.run()