import pygame
import math
import random
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Color definitions
DARK_PINK = (255, 51, 153)
LIGHT_PINK = (255, 182, 193)
WHITE = (255, 255, 255, 100)


class BeatingHeart:
    def __init__(self, width=800, height=600):
        # Window setup
        self.screen = pygame.display.set_mode((width, height), RESIZABLE)
        self.width, self.height = width, height
        self.clock = pygame.time.Clock()
        self.running = True

        # Heart parameters
        self.base_scale = 1.0  # Base scale
        self.beat_force = 0.15  # Beat strength
        self.beat_speed = 1.5  # Beat speed
        self.particle_count = 2000  # Number of particles

        # Initialize particle system
        self.particles = []
        self.init_particles()

        # Create semi-transparent surface for trail effect
        self.trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Heart shape points (parametric equation)
        self.heart_shape = self.generate_heart_shape()

    def generate_heart_shape(self, samples=300):
        """Generate base heart shape"""
        points = []
        t = 0
        while t < 2 * math.pi:
            x = 16 * (math.sin(t) ** 3)
            y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
            points.append((x, y))
            t += 2 * math.pi / samples
        return points

    def init_particles(self):
        """Initialize particle system"""
        self.particles = []
        for _ in range(self.particle_count):
            self.particles.append({
                'pos': [random.uniform(0, self.width),
                        random.uniform(0, self.height)],
                'vel': [0, 0],
                'target': (0, 0),
                'color': DARK_PINK
            })

    def calculate_beat(self):
        """Calculate heartbeat curve"""
        time = pygame.time.get_ticks() / 1000
        beat = math.sin(time * math.pi * self.beat_speed) * self.beat_force
        tremor = math.sin(time * 13) * 0.01  # Add slight tremor
        return self.base_scale * (1 + beat + tremor)

    def update_particles(self, scale):
        """Update particle states"""
        center_x, center_y = self.width // 2, self.height // 2

        for i, p in enumerate(self.particles):
            # Assign target point from heart shape
            heart_point = self.heart_shape[i % len(self.heart_shape)]
            target_x = center_x + heart_point[0] * 10 * scale
            target_y = center_y - heart_point[1] * 10 * scale

            # Calculate attraction
            dx = target_x - p['pos'][0]
            dy = target_y - p['pos'][1]
            distance = math.hypot(dx, dy)

            # Dynamic motion parameters
            speed = 0.08 + distance * 0.02
            friction = 0.92 - distance * 0.002

            # Update velocity, avoiding division by zero
            if distance > 1e-6:
                p['vel'][0] += dx / distance * speed
                p['vel'][1] += dy / distance * speed

            # Add random perturbation
            p['vel'][0] += random.uniform(-0.2, 0.2)
            p['vel'][1] += random.uniform(-0.2, 0.2)

            # Apply friction
            p['vel'][0] *= friction
            p['vel'][1] *= friction

            # Reset if velocity is invalid
            if math.isnan(p['vel'][0]) or math.isnan(p['vel'][1]):
                p['pos'] = [random.uniform(0, self.width), random.uniform(0, self.height)]
                p['vel'] = [0, 0]
            else:
                # Update position
                p['pos'][0] += p['vel'][0]
                p['pos'][1] += p['vel'][1]

            # Reset if position is invalid
            if math.isnan(p['pos'][0]) or math.isnan(p['pos'][1]):
                p['pos'] = [random.uniform(0, self.width), random.uniform(0, self.height)]

            # Clamp position to screen bounds
            p['pos'][0] = max(0, min(self.width, p['pos'][0]))
            p['pos'][1] = max(0, min(self.height, p['pos'][1]))

            # Color gradient based on Y position
            progress = (p['pos'][1] - (center_y - 150 * scale)) / (300 * scale)
            progress = max(0, min(1, progress))
            p['color'] = (
                int(DARK_PINK[0] + (LIGHT_PINK[0] - DARK_PINK[0]) * progress),
                int(DARK_PINK[1] + (LIGHT_PINK[1] - DARK_PINK[1]) * progress),
                int(DARK_PINK[2] + (LIGHT_PINK[2] - DARK_PINK[2]) * progress)
            )

    def draw(self, scale):
        """Draw particle heart"""
        # Trail effect
        self.trail_surface.fill((0, 0, 0, 15))  # Semi-transparent black for fading

        for p in self.particles:
            try:
                pos = (int(p['pos'][0]), int(p['pos'][1]))
                if 0 <= pos[0] < self.width and 0 <= pos[1] < self.height:
                    pygame.draw.circle(self.trail_surface, p['color'], pos, 2)
            except (TypeError, ValueError, OverflowError) as e:
                print(f"Error drawing particle: pos={p['pos']}, error={e}")
                continue

            # Draw trail
            for i in range(1, 4):
                alpha = 150 // i
                try:
                    pos = (
                        int(p['pos'][0] - p['vel'][0] * i),
                        int(p['pos'][1] - p['vel'][1] * i)
                    )
                    if 0 <= pos[0] < self.width and 0 <= pos[1] < self.height:
                        pygame.draw.circle(self.trail_surface,
                                           (*p['color'][:3], alpha), pos, max(1, 2 - i // 2))
                except (TypeError, ValueError, OverflowError) as e:
                    print(f"Error drawing trail: pos={p['pos']}, vel={p['vel']}, error={e}")
                    continue

        # Blit trail surface to screen
        self.screen.blit(self.trail_surface, (0, 0))

        # Add highlight effect
        for p in random.sample(self.particles, min(50, len(self.particles))):
            try:
                pos = (int(p['pos'][0]), int(p['pos'][1]))
                if 0 <= pos[0] < self.width and 0 <= pos[1] < self.height:
                    pygame.draw.circle(self.screen, WHITE[:3], pos, 2, 0)
                    pygame.draw.circle(self.screen, WHITE, pos, 4, 1)
            except (TypeError, ValueError, OverflowError):
                continue

    def run(self):
        """Main loop"""
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == VIDEORESIZE:
                    self.width, self.height = event.size
                    self.screen = pygame.display.set_mode((self.width, self.height), RESIZABLE)
                    self.trail_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    self.init_particles()

            # Calculate beat scale
            current_scale = self.calculate_beat()

            # Update and draw
            self.update_particles(current_scale)
            self.screen.fill((30, 30, 40))  # Dark background
            self.draw(current_scale)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    BeatingHeart().run()