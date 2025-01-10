import pygame

# Map
MAP_FILE = "maps/fall.json"

# Cartes
CARDS_FILE = "decks/base_deck.json"

# Dimensions de l'écran
WIDTH = 1920
HEIGHT = 1080

# Dimensions de la zone de plateau
BOARD_WIDTH = 1200  # 80% de la largeur
BOARD_HEIGHT = 600  # 80% de la hauteur

# Dimensions du panneau et de la zone des boutons d'actions
PANEL_WIDTH = WIDTH - BOARD_WIDTH  # 20% de la largeur
PANEL_HEIGHT = HEIGHT // 2  # 50% de la hauteur
ACTIONS_WIDTH = PANEL_WIDTH
ACTIONS_HEIGHT = HEIGHT // 2  # 50% de la hauteur

# Vitesse
ANIMATION_SPEED = 1

# Options d'affichage
FULLSCREEN = False

def get_screen_mode():
    if FULLSCREEN:
        return pygame.FULLSCREEN
    else:
        return 0