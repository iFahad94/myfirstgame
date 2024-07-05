import pygame
import math
# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Initialize Pygame
pygame.init()

# Set screen size
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Set caption
pygame.display.set_caption("Floating Enemy")

# Load enemy image (replace with your image path)
enemy_image = pygame.image.load("data\images\entities\enemy\idle\i0.png").convert_alpha()

# Define enemy class
class Enemy:
    def __init__(self, x, y, float_height=4, bob_amplitude=4, bob_speed=3):
        self.image = enemy_image
        self.rect = self.image.get_rect(center=(x, y))
        self.float_height = float_height
        self.bob_amplitude = bob_amplitude  # How much the enemy bobs up and down
        self.bob_speed = bob_speed  # Speed of the bobbing motion
        self.bob_offset = 0  # Current position in the bobbing cycle

    def update(self):
        # Make the enemy float above the surface
        self.rect.y = screen_height - self.image.get_height() - self.float_height

        # Bobbing motion
        self.bob_offset = (self.bob_offset + self.bob_speed) % 360  # Keep between 0 and 360 degrees
        self.rect.y += int(self.bob_amplitude * math.sin(math.radians(self.bob_offset)))
        print(self.rect.y)
    def draw(self, screen):
        screen.blit(self.image, self.rect)

# Create an enemy instance
enemy = Enemy(screen_width // 2, screen_height - enemy_image.get_height())  # Centered at the bottom

# Clock for frame rate control
clock = pygame.time.Clock()

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update objects
    enemy.update()

    # Fill the screen with black
    screen.fill(BLACK)

    # Draw objects
    enemy.draw(screen)

    # Update the display
    pygame.display.flip()

    # Set frame rate
    clock.tick(60)  # 60 FPS

# Quit Pygame
pygame.quit()
