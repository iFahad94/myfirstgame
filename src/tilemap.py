import json
import pygame

from src.utils import JSON_TYPE_STR, JSON_VARIANT_STR, JSON_POS_STR, TILE_SIZE, JSON_OFFGRID_STR
AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1),
                    (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'grass', 'stone', 'dungeon'}
AUTOTILE_TYPES = {'grass', 'stone', 'dungeon'}


class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []
        self.map_dims = []
        self.lvl = []
        
    def rect(self, pos, dir):
        if dir != None:
            if dir == "l":
                return pygame.Rect(pos[0] * TILE_SIZE, (pos[1] * TILE_SIZE) - TILE_SIZE,
                           TILE_SIZE, TILE_SIZE * 3)
            elif dir == "r":
                return pygame.Rect(pos[0] * TILE_SIZE, (pos[1] * TILE_SIZE) - TILE_SIZE,
                           TILE_SIZE, TILE_SIZE * 3)
            elif dir == "d":
                return pygame.Rect((pos[0] * TILE_SIZE) - TILE_SIZE, pos[1] * TILE_SIZE,
                           TILE_SIZE * 3, TILE_SIZE)
            elif dir == "u":
                return pygame.Rect((pos[0] * TILE_SIZE) - TILE_SIZE, pos[1] * TILE_SIZE,
                           TILE_SIZE * 3, TILE_SIZE)
            else:
                print("Invalid direction. Please choose r, l, u, or d.")
        return pygame.Rect(pos[0] * TILE_SIZE, (pos[1] * TILE_SIZE) - TILE_SIZE,
                           TILE_SIZE, TILE_SIZE * 3)
        
    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile[JSON_TYPE_STR], tile[JSON_VARIANT_STR]) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)

        for loc in self.tilemap.copy():
            tile = self.tilemap[loc]
            if (tile[JSON_TYPE_STR], tile[JSON_VARIANT_STR]) in id_pairs:
                matches.append(tile.copy())
                matches[-1][JSON_POS_STR] = matches[-1][JSON_POS_STR].copy()
                matches[-1][JSON_POS_STR][0] *= TILE_SIZE
                matches[-1][JSON_POS_STR][1] *= TILE_SIZE
                if not keep:
                    del self.tilemap[loc]
        return matches

    def save(self, path):
        f = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size,
                  'offgrid': self.offgrid_tiles, 'map_dims': self.map_dims}, f)
        f.close()

    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()

        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']
        self.map_dims = map_data['map_dims']
        self.lvl = map_data['lvl']

    def solid_check(self, pos):
        tile_loc = str(int(pos[0] // TILE_SIZE)) + \
            ';' + str(int(pos[1] // TILE_SIZE))
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc][JSON_TYPE_STR] in PHYSICS_TILES:
                return self.tilemap[tile_loc]
            
    def collide_nxt_lvl(self, player_rect):
        for nextlvl in self.lvl['next_lvl']:
            door_rect = self.rect(nextlvl['pos'], nextlvl['dir'])
            if door_rect.colliderect(player_rect):
                return nextlvl
        return None
    
    def nearby_tiles(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size),
                    int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + \
                ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles

    def nearby_tiles_rects(self, pos):
        rects = []
        for tile in self.nearby_tiles(pos):
            if tile[JSON_TYPE_STR] in PHYSICS_TILES:
                rects.append(
                    pygame.Rect(tile[JSON_POS_STR][0] * self.tile_size,
                                tile[JSON_POS_STR][1] * self.tile_size,
                                self.tile_size,
                                self.tile_size))
        return rects

    def autotile(self):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = str(tile[JSON_POS_STR][0] + shift[0]) + \
                    ';' + str(tile[JSON_POS_STR][1] + shift[1])
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc][JSON_TYPE_STR] == tile[JSON_TYPE_STR]:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile[JSON_TYPE_STR] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile[JSON_VARIANT_STR] = AUTOTILE_MAP[neighbors]

    def render(self, surf, offset=(0, 0)):
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile[JSON_TYPE_STR]][tile[JSON_VARIANT_STR]],
                      (tile[JSON_POS_STR][0] - offset[0],
                      tile[JSON_POS_STR][1] - offset[1]))
        for x in range(offset[0] // self.tile_size,
                       (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size,
                           (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    surf.blit(self.game.assets[tile[JSON_TYPE_STR]][tile[JSON_VARIANT_STR]],
                              (tile[JSON_POS_STR][0] * self.tile_size - offset[0],
                               tile[JSON_POS_STR][1] * self.tile_size - offset[1]))
