import pygame
import math
import random

from src.spark import Spark
from src.particle import Particle
from src.utils import (JSON_MAP_WIDTH_STR, JSON_MAP_HEIGHT_STR, SIZE_16, GRENADE_STR, SIZE_8, GRENADE_TIMER,
                       TILE_SIZE, PARTICLE_STR, PROJECTILE_SPEED, TYPE_ENEMY_STR, TYPE_PLAYER_STR)
from src.projectile import Projectile
from src.throwable import Throwable, Grenade


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False,
                           'right': False, 'left': False}

        self.action = ''
        self.anim_offset = (0, 0)
        self.flip = False
        self.set_action('idle')

        self.last_movement = [0, 0]

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1],
                           self.size[0], self.size[1])

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type +
                                              '/' + self.action].copy()

    def update(self, game, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False,
                           'right': False, 'left': False}
        frame_movement = (movement[0] + self.velocity[0],
                          movement[1] + self.velocity[1])

        self.pos[0] += frame_movement[0] * 2
        if not game.initializing or game.direction == 'u':
            entity_rect = self.rect()
            for rect in tilemap.nearby_tiles_rects(self.pos):
                if entity_rect.colliderect(rect):
                    if frame_movement[0] > 0:
                        entity_rect.right = rect.left
                        self.collisions['right'] = True
                    if frame_movement[0] < 0:
                        entity_rect.left = rect.right
                        self.collisions['left'] = True
                    self.pos[0] = entity_rect.x

            self.pos[1] += frame_movement[1]
            entity_rect = self.rect()
            for rect in tilemap.nearby_tiles_rects(self.pos):
                if entity_rect.colliderect(rect):
                    if frame_movement[1] > 0:
                        entity_rect.bottom = rect.top
                        self.collisions['down'] = True
                    if frame_movement[1] < 0:
                        entity_rect.top = rect.bottom
                        self.collisions['up'] = True
                    self.pos[1] = entity_rect.y

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.last_movement = movement

        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False),
                  (self.pos[0] - offset[0] + self.anim_offset[0],
                   self.pos[1] - offset[1] + self.anim_offset[1]))


class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)
        self.walking = 0

    def update(self, game, tilemap, movement=(0, 0)):
        if not game.initializing:
            if self.walking:
                if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                    if (self.collisions['right'] or self.collisions['left']):
                        self.flip = not self.flip
                    else:
                        movement = (
                            movement[0] - 0.5 if self.flip else 0.5, movement[1])
                else:
                    self.flip = not self.flip
                self.walking = max(0, self.walking - 1)
                # shooting logic
                if not self.walking:
                    dis = (
                        self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                    if (abs(dis[1]) < 30):
                        if (self.flip and dis[0] < 0):
                            self.game.projectiles.append(Projectile([self.rect(
                            ).centerx - 7, self.rect().centery], TYPE_ENEMY_STR, PROJECTILE_SPEED, game, False))
                            for i in range(4):
                                self.game.sparks.append(Spark(
                                    self.game.projectiles[-1].pos, random.random() - 0.5 + math.pi, 2 + random.random()))
                        if (not self.flip and dis[0] > 0):
                            self.game.projectiles.append(Projectile([self.rect(
                            ).centerx + 7, self.rect().centery], TYPE_ENEMY_STR, PROJECTILE_SPEED, game, True))
                            for i in range(4):
                                self.game.sparks.append(
                                    Spark(self.game.projectiles[-1].pos, random.random() - 0.5, 2 + random.random()))
            elif random.random() < 0.01:
                self.walking = random.randint(30, 60)

        super().update(game, tilemap, movement)

        if movement[0] != 0:
            self.set_action('walk')
        else:
            self.set_action('idle')

        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                self.game.screen_shake = max(16, self.game.screen_shake)
                for i in range(15):
                    angle = random.random() * math.pi * 2
                    self.game.sparks.append(
                        Spark(self.rect().center, angle, 2 + random.random(), (135, 23, 45)))
                return True

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset)
        gun = self.game.assets['gun']
        if self.flip:
            surf.blit(pygame.transform.flip(gun, True, False), (self.rect(
            ).centerx - 4 - gun.get_width() - offset[0], self.rect().bottom - 4 - offset[1]))
        else:
            surf.blit(gun, (self.rect().centerx + 10 - gun.get_width() -
                      offset[0], self.rect().bottom - 4 - offset[1]))


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 1
        self.is_wall_slide = False
        self.dashing = 0
        self.shooting = 0

    def update(self, game, tilemap, movement=(0, 0)):
        super().update(game, tilemap, movement)
        if not game.initializing:
            self.air_time += 1
            if self.collisions['down']:
                self.air_time = 0
                self.jumps = 1

            self.is_wall_slide = False
            if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
                self.is_wall_slide = True
                self.velocity[1] = min(self.velocity[1], 0.5)
                if self.collisions['right']:
                    self.flip = False
                else:
                    self.flip = True
                self.set_action('wall_slide')
                self.jumps = 1

            if not self.is_wall_slide:
                if self.air_time > 4:
                    self.set_action('jump')
                elif movement[0] != 0:
                    self.set_action('walk')
                else:
                    self.set_action('idle')

            if abs(self.dashing) in (60, 50):
                for i in range(4):
                    # The possible values for speed will be in the range of 0.628  (inclusive) to 6.28319 (inclusive).
                    angle = random.random() * math.pi * 2
                    # The possible values for speed will be in the range of 0.5 (inclusive) to 1.0 (inclusive).
                    speed = random.random() * 0.5 + 0.5
                    pvelocity = [math.cos(angle) * speed,
                                 math.sin(angle) * speed]

                    """ EXAMPLE OUTPUT: 
                    angle :  3.4700206235138893
                    speed :  0.5971471666139582
                    [math.cos(angle) :  -0.9465505797382577
                    [math.sin(angle) :  -0.3225554215901017
                    pvelocity :  [-0.5652299967475001, -0.1926130560785]`
                        """

                    self.game.particles.append(Particle(self.game, PARTICLE_STR, self.rect(
                    ).center, velocity=pvelocity, frame=random.randint(0, 7)))

            if self.dashing > 0:
                self.dashing = max(0, self.dashing - 1)
            else:
                self.dashing = min(0, self.dashing + 1)

            if abs(self.dashing) > 50:
                self.velocity[0] = abs(self.dashing) / self.dashing * 8
                if abs(self.dashing) == 51:
                    self.velocity[0] *= 0.3
                pvelocity = [abs(self.dashing) /
                             self.dashing * random.random() * 3, 0]
                self.game.particles.append(Particle(self.game, PARTICLE_STR, self.rect(
                ).center, velocity=pvelocity, frame=random.randint(0, 7)))

            if self.velocity[0] > 0:
                self.velocity[0] = max(self.velocity[0] - 0.1, 0)
            else:
                self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    def render(self, surf, offset=(0, 0)):
        if abs(self.dashing) <= 50:
            super().render(surf, offset)

    def jump(self):
        if self.is_wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 2
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = 2
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
        elif self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
            return True

    def dash(self):
        if not self.dashing:
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60

    def shoot(self):
        if self.flip:
            self.game.projectiles.append(Projectile([self.rect(
            ).centerx - 7, self.rect().centery], TYPE_PLAYER_STR, PROJECTILE_SPEED, self.game, False))
            for i in range(4):
                self.game.sparks.append(Spark(
                    self.game.projectiles[-1].pos, random.random() - 0.5 + math.pi, 2 + random.random()))
        else:
            self.game.projectiles.append(Projectile([self.rect(
            ).centerx + 7, self.rect().centery], TYPE_PLAYER_STR, PROJECTILE_SPEED, self.game, True))
            for i in range(4):
                self.game.sparks.append(
                    Spark(self.game.projectiles[-1].pos, random.random() - 0.5, 2 + random.random()))

    def throw(self):
        self.game.throwables.append(
            Grenade(self.game, self.pos, GRENADE_TIMER, GRENADE_STR, SIZE_8, self.flip))


class FloatingEnemy(PhysicsEntity):
    def __init__(self, game, pos, size, float_height=10, bob_amplitude=10, bob_speed=6):
        super().__init__(game, 'floatingEnemy', pos, size)
        self.float_height = float_height
        self.bob_amplitude = bob_amplitude  # How much the enemy bobs up and down
        self.bob_speed = bob_speed  # Speed of the bobbing motion
        self.bob_offset = 0  # Current position in the bobbing cycle
        self.walking = 0
        self.init_pos_x = pos[0]
        self.init_pos_y = pos[1]

    def update(self, game, tilemap, movement=(0, 0)):
        position_offset = self.init_pos_x - self.pos[0]
        if not game.initializing:
            if self.walking:
                if self.collisions['right'] or self.collisions['left'] or position_offset <= -60 or position_offset >= 60:
                    self.flip = not self.flip
                    self.init_pos_x = self.pos[0]
                else:
                    movement = (
                        movement[0] - 0.25 if self.flip else 0.25, movement[1])
                self.walking = max(0, self.walking - 1)
            elif random.random() < 0.1:
                self.walking = 60
        # Make the enemy float above the surface
        self.pos[1] = self.init_pos_y - self.size[1] - self.float_height

        # Bobbing motion
        # Keep between 0 and 360 degrees
        self.bob_offset = (self.bob_offset + self.bob_speed) % 360
        self.pos[1] += int(self.bob_amplitude *
                           math.sin(math.radians(self.bob_offset)))
        super().update(game, tilemap, movement)
        if movement[0] != 0:
            self.set_action('walk')
        else:
            self.set_action('idle')

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset)
