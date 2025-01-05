import pygame

# Map
MAP_FILE = "fall.json"

# Dimensions de l'écran
WIDTH = 1000
HEIGHT = 600

# Vitesse
ANIMATION_SPEED = 1

# Options d'affichage
FULLSCREEN = False

def get_screen_mode():
    if FULLSCREEN:
        return pygame.FULLSCREEN
    else:
        return 0