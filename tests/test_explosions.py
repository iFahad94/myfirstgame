import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Enhanced Explosion Effect')

# Colors
black = (0, 0, 0)
colors = [(255, 255, 224), (255, 255, 0), (255, 215, 0),
          (255, 165, 0), (255, 69, 0), (139, 0, 0)]


# Clock for controlling the frame rate
clock = pygame.time.Clock()
fps = 60

# Particle class


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(2, 6)
        self.color = random.choice(colors)
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(15, 35)
        self.vx = math.cos(self.angle) * self.speed
        self.vy = math.sin(self.angle) * self.speed
        self.alpha = 255

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 0.05  # Gravity effect
        self.alpha -= 3
        if self.alpha <= 0:
            return True
        return False

    def draw(self, screen):
        if self.alpha > 0:
            surface = pygame.Surface(
                (self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*self.color, self.alpha),
                               (self.radius, self.radius), self.radius)
            screen.blit(surface, (self.x - self.radius, self.y - self.radius))

# Explosion class


class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start_time = pygame.time.get_ticks()
        self.particles = [Particle(x, y) for _ in range(100)]
        self.flag = False

    def draw(self, screen, dt):
        for particle in self.particles:
            self.flag = particle.update(dt)
            particle.draw(screen)

        return self.flag

# Main loop


def main():
    running = True
    explosions = []

    while running:
        dt = clock.get_time() / 1000  # Convert to seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                explosions.append(Explosion(x, y))

        screen.fill(black)

        for explosion in explosions:
            if explosion.draw(screen, dt):
                explosions.remove(explosion)

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    main()
