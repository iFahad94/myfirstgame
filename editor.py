import sys

import pygame

from src.utils import load_images, TILE_SIZE, JSON_MAP_WIDTH_STR, JSON_MAP_HEIGHT_STR, MAIN_MAP, SCREEN_WIDTH, SCREEN_HEIGHT, DISPLAY_WIDTH, DISPLAY_HEIGHT
from src.tilemap import Tilemap

RENDER_SCALE = 2.0


class Editor:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('editor')
        self.main_display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.main_surface = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))

        self.clock = pygame.time.Clock()

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'spawners': load_images('tiles/spawners'),
            'dungeon': load_images('tiles/dungeon')
        }

        # Define font and text color for coordinates
        self.font = pygame.font.SysFont(None, 24)
        self.text_color = (255, 255, 255)  # White

        self.movement = [False, False, False, False]

        self.tilemap = Tilemap(self, tile_size=TILE_SIZE)

        try:
            # self.tilemap.load('data/maps/1.json')
            self.tilemap.load(MAIN_MAP)
        except FileNotFoundError:
            pass

        self.scroll = [0, 0]

        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0

        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.ongrid = True

        self.highest_x_pos = 0
        self.highest_y_pos = 0

        self.map_data = 0

    def run(self):
        while True:
            self.main_surface.fill((0, 0, 0))

            # Get mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Create text with coordinates for display
            coords_text = f"X: {mouse_x}, Y: {mouse_y}"
            text_surface = self.font.render(coords_text, True, self.text_color)

            # Calculate top right corner coordinates for text placement
            text_rect = text_surface.get_rect(topright=(600, 10))

            self.scroll[0] += (self.movement[1] - self.movement[0]) * 4
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 4

            if self.scroll[0] < 0:
                self.scroll[0] = 0
            if self.scroll[1] < 0:
                self.scroll[1] = 0

            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.tilemap.render(self.main_surface, offset=(render_scroll))

            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy(
            )
            current_tile_img.set_alpha(100)

            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
            tile_pos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size),
                        int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size))

            # try:
            #     print(self.tilemap.map_dims[JSON_MAP_WIDTH_STR])
            #     print(self.tilemap.map_dims[JSON_MAP_HEIGHT_STR])
            #     self.map_data = {"map_width": self.tilemap.map_dims[JSON_MAP_WIDTH_STR]
            #                     , "map_height": self.tilemap.map_dims[JSON_MAP_HEIGHT_STR]}
            # except:
            #     print('pass')
            if self.ongrid:
                self.main_surface.blit(
                    current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0], tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))
            else:
                self.main_surface.blit(current_tile_img, mpos)

            if self.clicking and self.ongrid:
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {
                    'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos}
                try:
                    self.highest_x_pos = max(
                        self.highest_x_pos, tile_pos[0] * TILE_SIZE, self.tilemap.map_dims[JSON_MAP_WIDTH_STR])
                    self.highest_y_pos = max(
                        self.highest_y_pos, tile_pos[1] * TILE_SIZE, self.tilemap.map_dims[JSON_MAP_HEIGHT_STR])
                except:
                    self.highest_x_pos = max(
                        self.highest_x_pos, tile_pos[0] * TILE_SIZE)
                    self.highest_y_pos = max(
                        self.highest_y_pos, tile_pos[1] * TILE_SIZE)

                self.map_data = {"map_width": self.highest_x_pos,
                                 "map_height": self.highest_y_pos}

            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos']
                                         [1] - self.scroll[1], tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                        self.tilemap.offgrid_tiles.remove(tile)

            self.main_surface.blit(current_tile_img, (5, 5))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group],
                                                               'variant': self.tile_variant,
                                                               'pos': (mpos[0] + self.scroll[0], mpos[1] + self.scroll[1])})
                    if event.button == 3:
                        self.right_clicking = True
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (
                                self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5:
                            self.tile_variant = (
                                self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4:
                            self.tile_group = (
                                self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (
                                self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                    if event.key == pygame.K_o:
                        self.tilemap.map_dims = self.map_data
                        self.tilemap.save('map.json')
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False

            # Draw coordinates text
            self.main_surface.blit(text_surface, text_rect)
            self.main_display.blit(
                pygame.transform.scale(self.main_surface, self.main_display.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)


Editor().run()
