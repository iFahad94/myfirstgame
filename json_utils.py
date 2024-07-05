import json

def get_lowest_xy(filename):
    lowest_x = float('inf')
    lowest_y = float('inf')

    with open(filename, 'r') as f:
        map_data = json.load(f)

    tilemap = map_data.get('tilemap')
    if not tilemap:
        print('Tilemap key is missing.')
        return None

    for key, value in tilemap.items():
        pos = value.get('pos')
        if isinstance(pos, (list, tuple)) and len(pos) == 2:
            x, y = pos
            if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                lowest_x = min(lowest_x, x)
                lowest_y = min(lowest_y, y)

    if lowest_x != float('inf') and lowest_y != float('inf'):
        return (lowest_x, lowest_y)
    else:
        return None

if __name__ == "__main__":
    filename = "map.json"
    lowest_coords = get_lowest_xy(filename)

    if lowest_coords:
        print(f"Lowest x,y coordinates: ({lowest_coords[0]}, {lowest_coords[1]})")
    else:
        print("No valid 'pos' entries found or coordinates are not numbers.")
