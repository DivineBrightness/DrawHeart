import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import random


class HeartParticle:
    def __init__(self, x, y, z, color=None):
        self.original_pos = np.array([x, y, z])
        self.position = np.array([x, y, z])
        self.size = random.uniform(1.5, 3.0)

        # 柔和的粉色系颜色
        if color is None:
            self.color = (
                random.uniform(0.8, 1.0),  # R
                random.uniform(0.3, 0.6),  # G
                random.uniform(0.4, 0.7),  # B
                random.uniform(0.6, 0.9)  # Alpha
            )
        else:
            self.color = color

    def update(self, time):
        # 微小的呼吸效果
        offset = 0.05 * math.sin(time * 3)
        self.position = self.original_pos + np.array([0, offset, offset])

    def draw(self):
        glPointSize(self.size)
        glColor4f(*self.color)
        glBegin(GL_POINTS)
        glVertex3f(*self.position)
        glEnd()


def generate_heart_particles(num_particles=2000):
    particles = []

    for _ in range(num_particles):
        # 复杂的心形参数方程
        u = random.uniform(0, 2 * np.pi)

        # 创建更精确的3D心形
        x = 16 * np.sin(u) ** 3 / 15
        y = (13 * np.cos(u) - 5 * np.cos(2 * u) - 2 * np.cos(3 * u) - np.cos(4 * u)) / 15
        z = np.sin(u) * np.cos(u) / 15

        # 随机轻微偏移，增加自然感
        x += random.uniform(-0.05, 0.05)
        y += random.uniform(-0.05, 0.05)
        z += random.uniform(-0.05, 0.05)

        particles.append(HeartParticle(x, y, z))

    return particles


def main():
    pygame.init()
    display = (1200, 800)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("💗 粒子爱心 💗")

    # OpenGL初始化
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # 透视设置
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    glTranslatef(0, 0, -3)

    # 生成粒子
    particles = generate_heart_particles()

    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

        current_time = (pygame.time.get_ticks() - start_time) / 1000.0

        # 清屏
        glClearColor(0.1, 0.1, 0.2, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        glTranslatef(0, 0, -3)

        # 旋转
        glRotatef(current_time * 20, 0, 1, 0)

        # 心跳缩放
        scale = 1 + 0.1 * math.sin(current_time * 3)
        glScalef(scale, scale, scale)

        # 更新和绘制粒子
        for particle in particles:
            particle.update(current_time)
            particle.draw()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()