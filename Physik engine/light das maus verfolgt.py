import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

particles = []

NUM_PARTICLES = 350

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.RESIZABLE
)

pygame.display.set_caption("Organic Growth")

clock = pygame.time.Clock()


class Particle:
    def __init__(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)

        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(0.5, 2)

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.size = random.randint(2, 5)
        self.color = (
            random.randint(100, 255),
            random.randint(120, 255),
            255
        )

        self.offset = random.uniform(0, 1000)

    def update(self, t):
        noise_x = math.sin(self.y * 0.01 + t * 0.002 + self.offset)
        noise_y = math.cos(self.x * 0.01 + t * 0.002 + self.offset)

        self.vx += noise_x * 0.03
        self.vy += noise_y * 0.03

        speed = math.sqrt(self.vx**2 + self.vy**2)

        max_speed = 2.5

        if speed > max_speed:
            self.vx = (self.vx / speed) * max_speed
            self.vy = (self.vy / speed) * max_speed

        self.x += self.vx
        self.y += self.vy

        if self.x < 0:
            self.x = WIDTH
        elif self.x > WIDTH:
            self.x = 0

        if self.y < 0:
            self.y = HEIGHT
        elif self.y > HEIGHT:
            self.y = 0

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            self.color,
            (int(self.x), int(self.y)),
            self.size
        )

for _ in range(NUM_PARTICLES):
    particles.append(Particle())

trail_surface = pygame.Surface((WIDTH, HEIGHT))
trail_surface.set_alpha(40)

running = True

while running:
    t = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(trail_surface, (0, 0))
    trail_surface.fill((0, 0, 0))

    for p in particles:
        p.update(t)
        p.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()