import pygame

# Dimensions de l'écran
WIDTH = 800
HEIGHT = 600

# Options d'affichage
FULLSCREEN = False

def get_screen_mode():
    if FULLSCREEN:
        return pygame.FULLSCREEN
    else:
        return 0