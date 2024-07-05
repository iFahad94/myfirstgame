import pygame
import random
import math

from src.utils import PROJECTILE_STR, TYPE_ENEMY_STR, TYPE_PLAYER_STR, DISPLAY_WIDTH, JSON_MAP_WIDTH_STR, TILE_SIZE
from src.spark import Spark


class Projectile:
    def __init__(self, pos, type, speed, game, flip):
        self.pos = list(pos)
        self.speed = speed
        self.type = type
        self.game = game
        self.flip = flip

    def update(self, tilemap):
        if self.flip:
            self.pos[0] += self.speed
        else:
            self.pos[0] -= self.speed

        for enemy in self.game.enemies.copy():
            if enemy.rect().collidepoint(self.pos) and self.type == TYPE_PLAYER_STR:
                self.game.enemies.remove(enemy)
                self.game.screen_shake = max(16, self.game.screen_shake)
                for i in range(15):
                    angle = random.random() * math.pi * 2
                    self.game.sparks.append(
                        Spark(enemy.rect().center, angle, 2 + random.random(), (135, 23, 45)))
                return 0
        if tilemap.solid_check(self.pos):
            for i in range(4):
                self.game.sparks.append(Spark(self.pos, random.random(
                ) - 0.5 + (math.pi if self.flip > 0 else 0), 2 + random.random()))
            return 0
        elif self.pos[0] > max(tilemap.map_dims[JSON_MAP_WIDTH_STR] + TILE_SIZE + 6, DISPLAY_WIDTH + 6) or self.pos[0] < 0:
            return 0
        elif abs(self.game.player.dashing) < 50:
            if self.game.player.rect().collidepoint(self.pos) and self.type == TYPE_ENEMY_STR:
                self.game.dead += 1
                self.game.screen_shake = max(16, self.game.screen_shake)
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    self.game.sparks.append(Spark(self.game.player.rect(
                    ).center, angle, 2 + random.random(), (135, 23, 45)))
                return 0
        return 1

    def render(self, surf, offset=(0, 0)):
        img = self.game.assets[PROJECTILE_STR]
        surf.blit(img, (self.pos[0] - img.get_width() / 2 - offset[0],
                  self.pos[1] - img.get_height() / 2 - offset[1]))
