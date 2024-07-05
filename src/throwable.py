import pygame

from src.utils import (BOUNCE_FACTOR, THROWABLE_VELOCITY_X, JSON_MAP_HEIGHT_STR, JSON_MAP_WIDTH_STR,
                       THROWABLE_VELOCITY_Y, GRAVITY, DISPLAY_WIDTH, DISPLAY_HEIGHT, SIZE_8)
from src.explosion import Explosion


class Throwable:
    def __init__(self, game, pos, timer, t_type, size=8, flip=False, frame=0):
        self.pos = list(pos)
        self.game = game
        self.size = size
        self.flip = flip
        self.velocityX = THROWABLE_VELOCITY_X
        self.velocityY = THROWABLE_VELOCITY_Y
        self.bounce = BOUNCE_FACTOR
        self.timer = timer
        self.animation = self.game.assets['throwable/' + t_type].copy()
        self.animation.frame = frame

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1],
                           self.size, self.size)

    def update(self, tilemap):
        if self.flip:
            self.pos[0] -= self.velocityX
        else:
            self.pos[0] += self.velocityX

        self.pos[1] += self.velocityY

        throwable_rect = self.rect()

        for rect in tilemap.nearby_tiles_rects(self.pos):
            if throwable_rect.colliderect(rect):
                # Check collision side (top, bottom, left, or right)
                collision_side = self.get_collision_side(throwable_rect, rect)

                # Handle collision based on side
                if collision_side == "top":
                    self.pos[1] = rect.top - self.size
                    self.velocityY *= -BOUNCE_FACTOR  # Bounce on ceiling
                elif collision_side == "bottom":
                    self.pos[1] = rect.bottom
                    self.velocityY = 0  # Stop bouncing on ground
                elif collision_side == "left":
                    self.pos[0] = rect.left - throwable_rect.width
                    self.velocityX *= -BOUNCE_FACTOR  # Bounce on left wall
                elif collision_side == "right":
                    self.pos[0] = rect.right
                    self.velocityX *= -BOUNCE_FACTOR  # Bounce on right wall
        if self.pos[0] + self.size >= max(tilemap.map_dims[JSON_MAP_WIDTH_STR] + SIZE_8, DISPLAY_WIDTH) or self.pos[1] + self.size >= max(tilemap.map_dims[JSON_MAP_HEIGHT_STR], DISPLAY_HEIGHT):
            return False

        if self.pos[0] <= 0:
            return False

        # Apply gravity
        self.velocityY += GRAVITY
        self.animation.update()

        if self.timer <= 0:
            self.game.explosions.append(Explosion(self.game, self.pos))
            return True
        else:
            self.timer = max(0, self.timer - 1)

    def render(self, surf, offset=(0, 0)):
        img = self.animation.img()
        resized_img = pygame.transform.scale(img, (8, 8))
        surf.blit(pygame.transform.flip(resized_img, self.flip, False),
                  (self.pos[0] - offset[0],
                   self.pos[1] - offset[1]))

    def get_collision_side(self, throwable_rect, tile_rect):

        throwable_x = throwable_rect.centerx
        tile_x = tile_rect.centerx
        throwable_y = throwable_rect.centery
        tile_y = tile_rect.centery

        dx = tile_x - throwable_x
        dy = tile_y - throwable_y

        if abs(dx) > abs(dy):
            if dx > 0:
                return "left"
            else:
                return "right"
        else:
            if dy > 0:
                return "top"
            else:
                return "bottom"


class Grenade(Throwable):
    def __init__(self, game, pos, timer, t_type, size=8, flip=False, frame=0):
        super().__init__(game, pos, timer, t_type, size, flip, frame)

    def update(self, tilemap):
        return super().update(tilemap)

    def render(self, surf, offset=(0, 0)):
        return super().render(surf, offset)
