import pygame

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Define screen dimensions
WIDTH = 800
HEIGHT = 600

# Define gravity and physics constants
GRAVITY = 0.3  # Adjust for desired gravity strength
# Adjust for bounce height (0 for no bounce, 1 for full bounce)
BOUNCE_FACTOR = 0.7
BALL_VELOCITY_X = 3  # Initial horizontal velocity to move right
BALL_VELOCITY_Y = -3  # Initial vertical velocity
BALL_RADIUS = 20  # Radius of the ball

# Initialize Pygame
pygame.init()
font = pygame.font.Font(None, 20)  # Use system fonts
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity Ball")
clock = pygame.time.Clock()

# Define a font for text rendering
font = pygame.font.Font(None, 20)  # Adjust font size as needed


class Ball:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.velocity_x = BALL_VELOCITY_X  # Initial horizontal velocity to move right
        self.velocity_y = BALL_VELOCITY_Y  # Initial vertical velocity

    def update(self):
       # Update ball position based on velocity
        self.x -= self.velocity_x
        self.y += self.velocity_y

        # Check for collisions with walls (right and bottom) and apply bounce
        if self.x + self.radius >= WIDTH:
            self.velocity_x *= -1  # Reverse horizontal velocity for bounce on right wall
        if self.y + self.radius >= HEIGHT:
            # Prevent sinking below the screen by setting the Y position to the bottom edge
            self.y = HEIGHT - self.radius
            # Invert vertical velocity for bounce on the bottom
            self.velocity_y *= -BOUNCE_FACTOR

        if self.x - self.radius <= 0:
            self.velocity_x *= -1  # Reverse horizontal velocity for bounce on right wall
        # Apply gravity
        self.velocity_y += GRAVITY

    def draw(self, screen):
        pygame.draw.circle(screen, self.color,
                           (int(self.x), int(self.y)), self.radius)


# Create the square and ball objects
ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS, GREEN)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Reset ball position and velocity when clicked
                ball.x = WIDTH // 2
                ball.y = HEIGHT // 2
                ball.velocity_x = BALL_VELOCITY_X  # Initial horizontal velocity to move right
                ball.velocity_y = BALL_VELOCITY_Y  # Initial vertical velocity

    # Clear the screen
    screen.fill(BLACK)
    # Update and draw the ball
    ball.update()
    ball.draw(screen)

    # Prepare text surfaces for ball attributes (using list comprehension for efficiency)
    attribute_texts = [
        font.render(f"X: {int(ball.x)}", True, WHITE),
        font.render(f"Y: {int(ball.y)}", True, WHITE),
        # Format velocity with 2 decimal places
        font.render(f"VX: {ball.velocity_x:.2f}", True, WHITE),
        # Format velocity with 2 decimal places
        font.render(f"VY: {ball.velocity_y:.2f}", True, WHITE)
    ]

    # Define text positions (adjust as needed)
    text_x = 10
    text_y_offset = 25
    for i, text in enumerate(attribute_texts):
        text_y = text_y_offset * (i + 1)  # Space out the text lines
        screen.blit(text, (text_x, text_y))

    # Update the display
    pygame.display.flip()

    # Set the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
