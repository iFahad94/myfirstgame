import sys
import pygame
import random
import math
import os
from src.utils import (resize_image, load_image, load_images, SCREEN_WIDTH, SCREEN_HEIGHT,
                       DISPLAY_WIDTH, DISPLAY_HEIGHT, PLAYER_SIZE_X, PLAYER_SIZE_Y, TILE_SIZE, Animation, JSON_MAP_WIDTH_STR, JSON_MAP_HEIGHT_STR,
                       JSON_LARGE_DECOR_STR, JSON_POS_STR, JSON_SPAWNER_STR,
                       LEAF_STR, FPS)
from src.clouds import Clouds
from src.entities import Player, FloatingEnemy
from src.tilemap import Tilemap
from src.particle import Particle
from src.rain import Rain


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("TEST STEADY CAM AND MOVE TO LVL 2")
        self.main_display = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.main_surface = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.clock = pygame.time.Clock()
        self.movement = [False, False]
        self.screen_shake = 0
        self.initializing = True
        self.next_lvl_transition = False

        self.assets = self.load_assets()
        self.background = resize_image(self.assets['background'])
        self.clouds = Clouds(self.assets['clouds'], count=4)
        self.rains = Rain(30)
        self.player = Player(self, (-14, 150 - 16),
                             (PLAYER_SIZE_X, PLAYER_SIZE_Y))
        self.tilemap = Tilemap(self, tile_size=TILE_SIZE)

        self.level = 0
        self.direction = 'l'
        self.load_level(self.level, self.direction)

    def load_assets(self):
        return {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('bg1.jpg'),
            'clouds': load_images('clouds'),
            'dungeon': load_images('tiles/dungeon'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=10),
            'enemy/walk': Animation(load_images('entities/enemy/walk'), img_dur=10),
            'floatingEnemy/idle': Animation(load_images('entities/floatingEnemy/idle'), img_dur=10),
            'floatingEnemy/walk': Animation(load_images('entities/floatingEnemy/walk'), img_dur=10),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=10),
            'player/walk': Animation(load_images('entities/player/walk'), img_dur=10),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'throwable/grenade': Animation(load_images('throwable/grenade'), img_dur=10),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
        }

    def load_level(self, level, direction):
        self.tilemap.load('data/maps/' + str(level) + '.json')
        self.leaf_spawners = [pygame.Rect(4 + tree[JSON_POS_STR][0], 4 + tree[JSON_POS_STR][1], 23, 13)
                              for tree in self.tilemap.extract([(JSON_LARGE_DECOR_STR, 2)], keep=True)]
        self.enemies = [FloatingEnemy(self, spawner[JSON_POS_STR], (PLAYER_SIZE_X, PLAYER_SIZE_Y))
                        for spawner in self.tilemap.extract([(JSON_SPAWNER_STR, 1)])]

        self.projectiles = []
        self.throwables = []
        self.particles = []
        self.sparks = []
        self.explosions = []

        self.scroll = [0, 0]
        self.dead = 0

        self.player.pos = [-14, 144]
        if self.direction != None:
            print(self.direction)
            if self.direction == "l":
                self.init_player(False, -14, 160, 28)
            elif self.direction == "r":
                self.init_player(True, 638, 160, 28)
            elif self.direction == "d":
                self.init_player(False, 320 - 30, 300 + 16, 28)
            elif self.direction == "u":
                self.init_player(False, 320 - 29, 0, 28)
            else:
                self.player.flip = False

        self.transition = -30

        self.initializing = True
        self.next_lvl_transition = False

    def run(self):
        while True:
            self.main_surface.blit(self.background, (0, 0))
            self.update_screen_shake()
            self.handle_level_transition()
            self.update_and_render_game_elements()
            self.handle_initialization()
            self.handle_events()
            self.render_transition()
            self.update_display()

    def init_player(self, flip, posX, posY, timer):
        self.player.flip = flip
        self.player.pos[0] = posX
        self.player.pos[1] = posY
        self.init_timer = timer

    def update_screen_shake(self):
        self.screen_shake = max(0, self.screen_shake - 1)

    def handle_level_transition(self):
        next_lvl = self.tilemap.collide_nxt_lvl(self.player.rect())
        if next_lvl is not None and not self.initializing:
            self.next_lvl_transition = True
            self.direction = next_lvl['next_dir']
        if self.next_lvl_transition and not self.initializing:
            self.transition += 1
            if self.transition > 30:
                self.level = min(
                    self.level + 1, len(os.listdir('data/maps')) - 1)
                self.load_level(self.level, self.direction)
        if self.transition < 0:
            self.transition += 1

    def update_and_render_game_elements(self):
        if self.dead:
            self.handle_death()

        render_scroll = self.handle_camera()

        self.update_leaf_spawners(render_scroll)
        self.tilemap.render(self.main_surface, offset=render_scroll)
        self.update_and_render_enemies(render_scroll)

        if not self.dead:
            self.player.update(self, self.tilemap,
                               (self.movement[1] - self.movement[0], 0))
            self.player.render(self.main_surface, offset=render_scroll)

        self.update_and_render_projectiles(render_scroll)
        self.update_and_render_sparks(render_scroll)
        self.update_and_render_throwables(render_scroll)
        self.update_and_render_explosions(render_scroll)
        self.update_and_render_particles(render_scroll)

    def handle_camera(self):
        if (self.player.rect().centerx + self.main_surface.get_width() / 2) <= (self.tilemap.map_dims[JSON_MAP_WIDTH_STR] + TILE_SIZE):
            self.scroll[0] += (self.player.rect().centerx -
                               self.main_surface.get_width() / 2 - self.scroll[0])
        if (self.player.rect().centery + self.main_surface.get_height() / 2) <= (self.tilemap.map_dims[JSON_MAP_HEIGHT_STR] + TILE_SIZE):
            self.scroll[1] += (self.player.rect().centery -
                               self.main_surface.get_height() / 2 - self.scroll[1])

        if self.scroll[0] < 0:
            self.scroll[0] = 0
        if self.scroll[1] < 0:
            self.scroll[1] = 0
        return (int(self.scroll[0]), int(self.scroll[1]))

    def handle_death(self):
        self.dead += 1
        if self.dead >= 10:
            self.transition = min(30, self.transition + 1)
        if self.dead > 60:
            self.load_level(self.level)

    def update_leaf_spawners(self, render_scroll):
        for rect in self.leaf_spawners:
            if random.random() * 30000 < rect.width * rect.height:
                pos = (rect.x + random.random() * rect.width,
                       rect.y + random.random() * rect.height)
                self.particles.append(Particle(self, LEAF_STR, pos, velocity=[
                                      random.random(), random.random()], frame=random.randint(0, 20)))

    def update_and_render_enemies(self, render_scroll):
        for enemy in self.enemies.copy():
            kill = enemy.update(self, self.tilemap, (0, 0))
            enemy.render(self.main_surface, offset=render_scroll)
            if kill:
                self.enemies.remove(enemy)

    def update_and_render_projectiles(self, render_scroll):
        for projectile in self.projectiles.copy():
            kill = projectile.update(self.tilemap)
            projectile.render(self.main_surface, offset=render_scroll)
            if kill == 0:
                self.projectiles.remove(projectile)

    def update_and_render_sparks(self, render_scroll):
        for spark in self.sparks.copy():
            kill = spark.update()
            spark.render(self.main_surface, offset=render_scroll)
            if kill:
                self.sparks.remove(spark)

    def update_and_render_throwables(self, render_scroll):
        for throwable in self.throwables.copy():
            kill = throwable.update(self.tilemap)
            throwable.render(self.main_surface, offset=render_scroll)
            if kill:
                self.throwables.remove(throwable)

    def update_and_render_explosions(self, render_scroll):
        for explosion in self.explosions.copy():
            dt = self.clock.get_time() / 1000
            kill = explosion.update(dt)
            explosion.render(self.main_surface, offset=render_scroll)
            if kill:
                self.explosions.remove(explosion)

    def update_and_render_particles(self, render_scroll):
        for particle in self.particles.copy():
            kill = particle.update()
            particle.render(self.main_surface, offset=render_scroll)
            if particle.type == LEAF_STR:
                particle.pos[0] += math.sin(
                    particle.animation.frame * 0.035) * 0.3
            if kill:
                self.particles.remove(particle)

    def handle_initialization(self):
        if self.initializing and not self.player.flip and self.direction in ('l'):
            self.player.pos[0] += 0.5
            if self.init_timer <= 0:
                self.initializing = False
            self.init_timer = max(0, self.init_timer - 1)
        elif self.initializing and self.player.flip and self.direction in ('r'):
            self.player.pos[0] -= 0.5
            if self.init_timer <= 0:
                self.initializing = False
            self.init_timer = max(0, self.init_timer - 1)
        elif self.initializing and not self.player.flip and self.direction in ('d'):
            self.player.pos[1] += -0.2
            self.player.pos[0] += 0.8
            if self.init_timer <= 0:
                self.initializing = False
            self.init_timer = max(0, self.init_timer - 1)
        elif self.initializing and not self.player.flip and self.direction in ('u'):
            if self.init_timer <= 0:
                self.initializing = False
            self.init_timer = max(0, self.init_timer - 1)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                self.handle_keydown(event)
            if event.type == pygame.KEYUP:
                self.handle_keyup(event)

    def handle_keydown(self, event):
        if event.key == pygame.K_LEFT:
            self.movement[0] = True
        if event.key == pygame.K_RIGHT:
            self.movement[1] = True
        if event.key == pygame.K_UP:
            self.player.jump()
        if event.key == pygame.K_x:
            self.player.dash()
        if event.key == pygame.K_c:
            self.player.throw()
        if event.key == pygame.K_z:
            self.player.shoot()

    def handle_keyup(self, event):
        if event.key == pygame.K_LEFT:
            self.movement[0] = False
        if event.key == pygame.K_RIGHT:
            self.movement[1] = False

    def render_transition(self):
        if self.transition:
            transition_surf = pygame.Surface(self.main_surface.get_size())
            pygame.draw.circle(transition_surf, (255, 255, 255), (self.main_surface.get_width(
            ) // 2, self.main_surface.get_height() // 2), (30 - abs(self.transition)) * 8)
            transition_surf.set_colorkey((255, 255, 255))
            self.main_surface.blit(transition_surf, (0, 0))

    def update_display(self):
        screenshake_offset = (random.random() * self.screen_shake - self.screen_shake / 2,
                              random.random() * self.screen_shake - self.screen_shake / 2)
        self.main_display.blit(pygame.transform.scale(
            self.main_surface, self.main_display.get_size()), screenshake_offset)
        pygame.display.update()
        self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()
