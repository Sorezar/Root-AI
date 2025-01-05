import pygame
import config

COLORS = {
    "forests": (34, 139, 34),       # Vert forêt
    "nodes": (255, 255, 255),       # Blanc pour les clairières
    "edges": (0, 0, 0),             # Noir pour les connexions
    "rivers": (0, 0, 255),          # Bleu pour les rivières
    "text": (0, 0, 0),              # Noir pour le texte
    "control": (0, 0, 0),           # Noir pour le contrôle par défaut
    "background": (245, 245, 220),  # Beige pour le fond
    "units": {"Marquise de Chat": (255, 165, 0), "Alliance": (0, 255, 0)},
    "buildings": {"default": (128, 128, 128)}
}

SYMBOL_COLORS = {
    "Renard": (255, 0, 0),    # Rouge pour les renards
    "Lapin":  (255, 255, 0),  # Jaune pour les lapins
    "Souris": (255, 165, 0),  # Orange pour les souris
}

# Dimensions
WIDTH, HEIGHT = config.WIDTH, config.HEIGHT
NODE_RADIUS = 30
UNIT_RADIUS = 10
SYMBOL_SIZE = 12
CONTROL_RADIUS = NODE_RADIUS
BUILDING_RADIUS = 15

class RootDisplay:
    def __init__(self, board):
        self.board = board
        pygame.init()
        pygame.display.set_caption("Root")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), config.get_screen_mode())
        self.clock  = pygame.time.Clock()
        self.font   = pygame.font.SysFont(None, 24)
        self.unit_font = pygame.font.SysFont(None, 18)

    def draw_board(self):
        # Remplir l'écran avec la couleur de fond beige
        self.screen.fill(COLORS["background"])
        
        nodes, edges, rivers = self.board.get_nodes_and_edges()
        
        # Dessine les connexions (arêtes)
        for edge in edges:
            pos1 = nodes[edge[0] - 1][1]["pos"]
            pos2 = nodes[edge[1] - 1][1]["pos"]
            pygame.draw.line(self.screen, COLORS["edges"], pos1, pos2, 3)
        
        # Dessine la rivière
        for river in rivers:
            pos1 = nodes[river[0] - 1][1]["pos"]
            pos2 = nodes[river[1] - 1][1]["pos"]
            pygame.draw.line(self.screen, COLORS["rivers"], pos1, pos2, 3)

        # Dessine les clairières et les unités
        for node, data in nodes:
            pos = data["pos"]
            
            # Dessine la clairière
            pygame.draw.circle(self.screen, COLORS["nodes"], pos, NODE_RADIUS)
            text = self.font.render(str(node), True, COLORS["text"])
            self.screen.blit(text, (pos[0] - 10, pos[1] - 10))
            
            # Dessine le cercle de contrôle
            control_color = COLORS["control"]
            if data["control"]:
                control_color = COLORS["units"].get(data["control"], COLORS["control"])
            pygame.draw.circle(self.screen, control_color, pos, CONTROL_RADIUS, 3)

            # Dessine le symbole graphique de type de clairière
            clearing_type = data["type"]
            if clearing_type in SYMBOL_COLORS:
                symbol_pos = (pos[0] + NODE_RADIUS - 10, pos[1] + NODE_RADIUS - 10)
                pygame.draw.circle(self.screen, SYMBOL_COLORS[clearing_type], symbol_pos, SYMBOL_SIZE // 2)

            # Dessine les unités dans la clairière
            offset = -20  # Décalage initial pour la première unité
            for faction, count in data["units"].items():
                faction_color = COLORS["units"].get(faction, (200, 200, 200))
                unit_pos = (pos[0] + offset, pos[1])
                pygame.draw.circle(self.screen, faction_color, unit_pos, UNIT_RADIUS)
                
                # Affiche le nombre d'unités
                unit_text = self.unit_font.render(str(count), True, COLORS["text"])
                self.screen.blit(unit_text, (unit_pos[0] - 5, unit_pos[1] - 5))
                offset += 15 # Décalage pour les unités suivantes

            # Dessine les bâtiments dans la clairière
            offset = -20  # Décalage initial pour le premier bâtiment
            for building_type, faction in data["buildings"].items():
                building_color = COLORS["units"].get(faction, COLORS["buildings"]["default"])
                building_pos = (pos[0] + offset, pos[1] + 20)
                pygame.draw.circle(self.screen, building_color, building_pos, BUILDING_RADIUS)
                offset += 20  # Décalage pour les bâtiments suivants
                
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        pygame.display.toggle_fullscreen()

            self.draw_board()
            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()