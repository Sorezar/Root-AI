import pygame

# Map
MAP_FILE = "maps/fall.json"

# Cartes
CARDS_FILE = "decks/base_deck.json"

# Dimensions de l'écran
WIDTH = 1920
HEIGHT = 1080

# Zone Joueurs
PLAYERS_X = 0
PLAYERS_Y = 0
PLAYERS_WIDTH  = 1 * WIDTH
PLAYERS_HEIGHT = 0.22 * HEIGHT

# Zone Items
ITEMS_ZONE_X = 0
ITEMS_ZONE_Y = 0.22 * HEIGHT
ITEMS_ZONE_WIDTH  = 0.2 * WIDTH
ITEMS_ZONE_HEIGHT = 0.1 * HEIGHT

# Zone Historique
HISTORY_X = 0
HISTORY_Y = 0.32 * HEIGHT
HISTORY_WIDTH  = 0.2 * WIDTH
HISTORY_HEIGHT = 0.68 * HEIGHT

# Zone Plateau
BOARD_X = 0.2 * WIDTH
BOARD_Y = 0.22 * HEIGHT
BOARD_WIDTH  = 0.6 * WIDTH 
BOARD_HEIGHT = 0.53 * HEIGHT

# Zone Cartes
CARDS_ZONE_X = 0.2 * WIDTH
CARDS_ZONE_Y = 0.75 * HEIGHT
CARDS_ZONE_WIDTH  = 0.6 * WIDTH
CARDS_ZONE_HEIGHT = 0.25 * HEIGHT

# Zone Cartes craftées
CRAFTED_CARDS_ZONE_X = 0.8 * WIDTH
CRAFTED_CARDS_ZONE_Y = 0.32 * HEIGHT
CRAFTED_CARDS_ZONE_WIDTH  = 0.2 * WIDTH
CRAFTED_CARDS_ZONE_HEIGHT = 0.43 * HEIGHT

# Zone Items craftées
CRAFTED_ITEMS_ZONE_X = 0.8 * WIDTH
CRAFTED_ITEMS_ZONE_Y = 0.22 * HEIGHT
CRAFTED_ITEMS_ZONE_WIDTH  = 0.2 * WIDTH
CRAFTED_ITEMS_ZONE_HEIGHT = 0.1 * HEIGHT

# Zone Actions et bouton fin de tour
ACTIONS_ZONE_X = 0.8 * WIDTH
ACTIONS_ZONE_Y = 0.75 * HEIGHT
ACTIONS_ZONE_WIDTH  = 0.2 * WIDTH
ACTIONS_ZONE_HEIGHT = 0.25 * HEIGHT

SCALE = min(WIDTH / 1920, HEIGHT / 1080)

# Tailles des éléments
CARDS_WIDTH  = 195 * SCALE
CARDS_HEIGHT = 260 * SCALE
CARDS_PLAYERS_WIDTH  = 70 * SCALE
CARDS_PLAYERS_HEIGHT = 95 * SCALE
CRAFTED_CARDS_WIDTH_4  = 154 * SCALE
CRAFTED_CARDS_HEIGHT_4 = 210 * SCALE
CRAFTED_CARDS_WIDTH_6  = 95 * SCALE
CRAFTED_CARDS_HEIGHT_6 = 129 * SCALE

NODE_RADIUS    = 50 * SCALE
UNIT_RADIUS    = 12 * SCALE
SYMBOL_SIZE    = 25 * SCALE
BUILDING_SIZE  = 22 * SCALE
TOKEN_SIZE     = 22 * SCALE
ITEM_SIZE      = 40 * SCALE
ICON_SIZE      = 40 * SCALE
ACTIONS_SIZE   = 60 * SCALE
 
# Couleurs
COLORS = {
    "forests":    (34, 139, 34),    # Vert forêt
    "nodes":      (255, 255, 255),  # Blanc pour les clairières
    "edges":      (0, 0, 0),        # Noir pour les connexions
    "rivers":     (119,181,254),    # Bleu pour les rivières
    "text":       (0, 0, 0),        # Noir pour le texte
    "control":    (0, 0, 0),        # Noir pour le contrôle par défaut
    "background": (245, 245, 220),  # Beige pour le fond
    "panel_bg":   (200, 200, 200),  # Gris clair pour les panneaux
    "slots":      (230, 230, 230),  # Gris clair pour les emplacements vides
    "borders":    (139, 69, 19),    # Brun pour les bordures
    "units": 
    {
        0 : (255, 165, 0),          # Orange pour la Marquise
        1 : (0, 0, 255),            # Bleu pour la Canopée
        2 : (0, 128, 0),            # Vert sapin pour l'Alliance
        3 : (190, 190, 190),        # Gris pour le Vagabond
    },
    "text_units": 
    {
        0 : (0, 0, 0),              # Noir pour la Marquise
        1 : (255, 255, 255),        # Blanc pour la Canopée
        2 : (0, 0, 0),              # Noir pour l'Alliance
        3 : (0, 0, 0),              # Noir pour le Vagabond
    }
}

# Vitesse
ANIMATION_SPEED = 1