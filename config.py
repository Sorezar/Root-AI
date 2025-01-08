import pygame

# Map
MAP_FILE = "maps/fall.json"

# Cartes
CARDS_FILE = "decks/base_deck.json"

# Dimensions de l'écran
WIDTH = 1920
HEIGHT = 1080

# Vitesse
ANIMATION_SPEED = 1

# Options d'affichage
FULLSCREEN = False

def get_screen_mode():
    if FULLSCREEN:
        return pygame.FULLSCREEN
    else:
        return 0