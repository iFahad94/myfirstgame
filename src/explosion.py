import pygame
import random
import math

from src.utils import EXPLOSION_GRENADE_COLORS, SIZE_16
from src.spark import Spark

# Explosion class


class Explosion:
    def __init__(self, game, pos):
        self.pos = list(pos)
        self.game = game
        self.particles = [Particle(self.pos[0], self.pos[1])
                          for _ in range(20)]
        self.flag = False
        self.effect_timer = 30

    def rect(self):
        return pygame.Rect(self.pos[0] - SIZE_16, self.pos[1] - SIZE_16,
                           SIZE_16, SIZE_16)
        
    def update(self, dt):
        for particle in self.particles:
            self.flag = particle.update(dt)
            for enemy in self.game.enemies.copy():
                if enemy.rect().colliderect(self.rect()):
                    if self.effect_timer >= 0:
                        self.game.enemies.remove(enemy)
                        self.game.screen_shake = max(16, self.game.screen_shake)
                        for i in range(15):
                            angle = random.random() * math.pi * 2
                            self.game.sparks.append(
                                Spark(enemy.rect().center, angle, 2 + random.random(), (135, 23, 45)))
                        return 0
                    else:
                        self.effect_timer = max(0, self.effect_timer - 1)
            if self.flag:
                self.particles.remove(particle)
        return self.flag

    def render(self, surf, offset=(0, 0)):
        for particle in self.particles:
            particle.render(surf, offset)

# Particle class


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(2, 6)
        self.color = random.choice(EXPLOSION_GRENADE_COLORS)
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(5, 15)
        self.vx = math.cos(self.angle) * self.speed
        self.vy = math.sin(self.angle) * self.speed
        self.alpha = 255

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 0.05  # Gravity effect
        self.alpha -= 7
        if self.alpha <= 0:
            return True
        return False

    def render(self, surf, offset=(0, 0)):
        if self.alpha > 0:
            surface = pygame.Surface(
                (self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*self.color, self.alpha),
                               (self.radius, self.radius), self.radius)
            surf.blit(surface, (self.x - self.radius -
                      offset[0], self.y - self.radius - offset[1]))
