import json
import os

class SaveLoadManager:
    def __init__(self, filename='savegame.json'):
        self.filename = filename

    def save_game(self, player, game):
        data = {
            'position': {
                'x': player.rect.x,
                'y': player.rect.y
            },
            'score': player.score,
            'lvl': game.level,
            'inventory': {
                'pistol_ammo': player.ammo,
                'grenade': player.grenade
            }
        }
        with open(self.filename, 'w') as file:
            json.dump(data, file)

    def load_game(self, player):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                data = json.load(file)
                player.rect.x = data['position']['x']
                player.rect.y = data['position']['y']
                player.score = data['score']
