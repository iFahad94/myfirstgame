import math
import random

from src.utils import DISPLAY_WIDTH, DISPLAY_HEIGHT, JSON_MAP_WIDTH_STR, JSON_MAP_HEIGHT_STR
import pygame

class RainDrop:
    def __init__(self, pos, color=(200,200,200)):
        self.pos = list(pos)
        self.color = color
        self.length = random.randint(2, 8)
        self.speed = random.randint(2, 8)
        self.drift = random.uniform(0.5, 1)  # Slight right movement
        self.alpha = random.randint(100, 150)  # Transparency
        
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], 
                           1, 1)
        
    def reset_pos(self):
        self.pos[0] = random.randint(0, DISPLAY_WIDTH - 10)
        self.pos[1] = random.randint(-150, -10)
        
    def update(self, tilemap):
        self.pos[0] += self.drift
        self.pos[1] += self.speed
                
        if self.pos[1] >= max(tilemap.map_dims[JSON_MAP_HEIGHT_STR], DISPLAY_HEIGHT) or self.pos[0] >= max(tilemap.map_dims[JSON_MAP_WIDTH_STR], DISPLAY_WIDTH):
            self.reset_pos()
        for rect in tilemap.nearby_tiles_rects(self.pos):
            if self.rect().colliderect(rect):
                # self.reset_pos()
                return True
    
        return False
    
    def render(self, surf, offset=(0, 0)):
        # Create a semi-transparent surface for raindrops
        drop_surface = pygame.Surface((2, self.length), pygame.SRCALPHA)
        drop_color = (200,200,200, self.alpha)
        pygame.draw.line(drop_surface, drop_color, (1, 0), (1, self.length))
        surf.blit(drop_surface, (self.pos[0] - offset[0], self.pos[1] - offset[1]))
        
# Raindrop class
class Rain:
    def __init__(self, count = 30):
        self.raindrops = []
        self.splashes = []
        
        for i in range(count):
            self.raindrops.append(RainDrop((random.randint(0, DISPLAY_WIDTH), random.randint(-150, -10))))        
    
    def update(self, tilemap):
        for i in range(len(self.raindrops)):
            if self.raindrops[i].update(tilemap):
                self.splashes.append(Splash(self.raindrops[i].pos))
                self.raindrops[i].reset_pos()

        for splash in self.splashes:
            splash.update()
            if not splash.particles:
                self.splashes.remove(splash)
                
    def render(self, surf, offset=(0, 0)):
        for raindrop in self.raindrops:
            raindrop.render(surf, offset=offset)
        for splash in self.splashes:
            splash.render(surf, offset=offset)
            
class Splash:
    def __init__(self, pos):
        self.particles = [SplashParticle((pos[0], pos[1])) for _ in range(random.randint(5, 10))]
        
    def update(self):
        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if p.alpha > 0]
    
    def render(self, surf, offset=(0, 0)):
        for particle in self.particles:
            particle.render(surf, offset)
    
# SplashParticle class
class SplashParticle:
    def __init__(self,pos, colors=(200,200,200)):
        self.pos = list(pos)
        self.colors = list(colors)
        self.alpha = 255
        self.radius = random.randint(1, 3)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-1, -3)
        
    def update(self):
        self.pos[0] += self.vx
        self.pos[1] += self.vy
        self.alpha -= 20
        if self.alpha < 0:
            self.alpha = 0
            
    def render(self, surf, offset=(0, 0)):
        if self.alpha > 0:
            splash_surface = pygame.Surface((self.radius * 1.2, self.radius * 1.2), pygame.SRCALPHA)
            splash_surface.set_alpha(self.alpha)
            pygame.draw.circle(splash_surface, (200, 200, 200, self.alpha), (self.radius, self.radius), self.radius)
            surf.blit(splash_surface, (self.pos[0] - self.radius - offset[0], self.pos[1] - self.radius - offset[1]))