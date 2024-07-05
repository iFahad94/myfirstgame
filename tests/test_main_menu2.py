import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sci-Fi Runner")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYBERPUNK_PINK = (255, 0, 255)
CYBERPUNK_BLUE = (0, 255, 255)
CYBERPUNK_PURPLE = (128, 0, 128)
VAPORWAVE_PINK = (255, 105, 180)
VAPORWAVE_CYAN = (0, 255, 255)
VAPORWAVE_PURPLE = (255, 20, 147)

# Font settings
FONT_PATH = 'tests/font.ttf'
FONT_SIZE = 24
font = pygame.font.Font(FONT_PATH, FONT_SIZE)
TITLE_FONT_SIZE = 48
title_font = pygame.font.Font(FONT_PATH, TITLE_FONT_SIZE)

class Button:
    def __init__(self, text, x, y, color, hover_color, action=None):
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.rect = None
        self.x = x
        self.y = y

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.hover_color if self.is_hovered(mouse_pos) else self.color
        text_surface = font.render(self.text, True, current_color)
        self.rect = text_surface.get_rect(center=(self.x, self.y))
        screen.blit(text_surface, self.rect)

    def is_hovered(self, mouse_pos):
        if self.rect and self.rect.collidepoint(mouse_pos):
            return True
        return False

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect and self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()

class MainMenu:
    def __init__(self):
        self.title_text = "Sci-Fi Runner"
        self.buttons = [
            Button("Start", SCREEN_WIDTH//2, 250, CYBERPUNK_BLUE, VAPORWAVE_CYAN, self.start_game),
            Button("Load", SCREEN_WIDTH//2, 300, CYBERPUNK_PINK, VAPORWAVE_PINK, self.load_game),
            Button("Options", SCREEN_WIDTH//2, 350, CYBERPUNK_PURPLE, VAPORWAVE_PURPLE, self.options_menu),
            Button("Quit", SCREEN_WIDTH//2, 400, CYBERPUNK_BLUE, VAPORWAVE_CYAN, self.quit_game)
        ]

    def start_game(self):
        print("Start Game")

    def load_game(self):
        print("Load Game")

    def options_menu(self):
        print("Options Menu")

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def run(self):
        running = True
        while running:
            screen.fill(BLACK)

            # Draw title
            title_surface = title_font.render(self.title_text, True, CYBERPUNK_PURPLE)
            title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 150))
            screen.blit(title_surface, title_rect)

            # Draw buttons
            for button in self.buttons:
                button.draw(screen)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                for button in self.buttons:
                    button.is_clicked(event)

            pygame.display.flip()

# Main execution
if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
