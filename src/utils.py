import os
import pygame

BASE_IMG_PATH = 'data/images/'
SPEED = 2
# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 700
DISPLAY_WIDTH = 640
DISPLAY_HEIGHT = 350

TILE_SIZE = 16

SIZE_16 = 16
SIZE_8 = 8

PLAYER_SIZE_X = 13
PLAYER_SIZE_Y = 16

MAIN_MAP = 'map.json'

JSON_TILEMAP_STR = 'tilemap'
JSON_TYPE_STR = 'type'
JSON_VARIANT_STR = 'variant'
JSON_DECOR_STR = 'decor'
JSON_LARGE_DECOR_STR = 'large_decor'
JSON_SPAWNER_STR = 'spawners'
JSON_POS_STR = 'pos'
JSON_TILE_SIZE_STR = 'tile_size'
JSON_OFFGRID_STR = 'offgrid'
JSON_MAP_DIMS_STR = 'map_dims'
JSON_MAP_WIDTH_STR = 'map_width'
JSON_MAP_HEIGHT_STR = 'map_height'

UP_STR = 'up'
LEFT_STR = 'left'
RIGHT_STR = 'right'
BOTTOM_STR = 'bottom'
PARTICLE_STR = 'particle'
PROJECTILE_STR = 'projectile'
LEAF_STR = 'leaf'
GRENADE_STR = 'grenade'

TYPE_ENEMY_STR = 'enemy'
TYPE_PLAYER_STR = 'player'

FPS = 60

PROJECTILE_SPEED = 2.5

# Define gravity and physics constants
GRAVITY = 0.1  # Adjust for desired gravity strength
# Adjust for bounce height (0 for no bounce, 1 for full bounce)
BOUNCE_FACTOR = 0.7
THROWABLE_VELOCITY_X = 1.5  # Initial horizontal velocity to move right
THROWABLE_VELOCITY_Y = -2  # Initial vertical velocity

GRENADE_TIMER = 120

EXPLOSION_GRENADE_COLORS = [
    (255, 0, 0), (255, 165, 0), (255, 255, 0), (255, 140, 0)]


def load_image(path):
    image = pygame.image.load(BASE_IMG_PATH + path).convert()
    image.set_colorkey((0, 0, 0))
    return image


def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images


def resize_background(display_size, background_size):
    screen_width, screen_height = display_size
    display_width, display_height = background_size

    # Calculate the ratio that maintains aspect ratio while fitting the screen width
    scale_factor_x = screen_width / display_width

    # Calculate the ratio that maintains aspect ratio while fitting the screen height
    scale_factor_y = screen_height / display_height

    # Choose the smaller scaling factor to avoid stretching in either dimension
    return min(scale_factor_x, scale_factor_y)


def resize_image(image):

    # Get the original image dimensions
    original_width, original_height = image.get_size()

    # Calculate the aspect ratio to maintain proportions
    aspect_ratio = original_width / original_height

    # Determine the new width and height based on the surface dimensions
    # and maintaining aspect ratio
    if DISPLAY_WIDTH / aspect_ratio <= DISPLAY_HEIGHT:
        new_width = DISPLAY_WIDTH
        new_height = int(DISPLAY_WIDTH / aspect_ratio)
    else:
        new_height = DISPLAY_HEIGHT
        new_width = int(DISPLAY_HEIGHT * aspect_ratio)

    # Resize the image using smooth scaling for better quality
    resized_image = pygame.transform.smoothscale(
        image, (DISPLAY_WIDTH, DISPLAY_HEIGHT))

    # Quit Pygame (optional, especially if not using it elsewhere)
    # pygame.quit()

    return resized_image


class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.is_done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)

    def img(self):
        return self.images[int(self.frame / self.img_duration)]

    def update(self):
        if self.loop:
            self.frame = (
                self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(
                self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.is_done = True


#     Example Input and Output:

# Case 1: Looping Animation (self.loop = True, self.img_duration = 5, 3 images)

# Initial Frame (self.frame = 0):

#     Looping condition is met, so the frame is incremented by 0.5: self.frame = 0 + 0.5 = 0.5
#     Modulo operation wraps it around: self.frame = 0.5 % (5 * 3) = 0.5

# Subsequent Frames:

#     Each iteration continues incrementing by 0.5 and wrapping around:
#         1.0 % 15 = 1.0
#         1.5 % 15 = 1.5
#         2.0 % 15 = 2.0

# Output:

#     The animation continuously loops through the 3 images, displaying each for 5 frames (due to self.img_duration).

# Case 2: Non-Looping Animation (self.loop = False, self.img_duration = 3, 4 images)

# Initial Frame (self.frame = 0):

#     No looping, so the frame is incremented by 1: self.frame = 0 + 1 = 1

# Subsequent Frames:

#     Each iteration increments by 1, capped at the maximum index:
#         self.frame = 1 + 1 = 2
#         self.frame = min(2 + 1, 3 * 4 - 1) = 3 (capped at the last frame)
#         The loop exits because self.frame reaches the maximum.

# Output:

#     The animation plays through the 4 images once, displaying each for 3 frames (due to self.img_duration) and then stops (self.done = True).

# Key Points:

#     The modulo operator (%) ensures smooth looping transitions by wrapping around.
#     The min() function prevents the frame index from exceeding the maximum.
#     The self.done flag signals the end of a non-looping animation.
