import pygame
import config

COLORS = {
    "forests": (34, 139, 34),       # Vert forêt
    "nodes": (255, 255, 255),       # Blanc pour les clairières
    "edges": (0, 0, 0),             # Noir pour les connexions
    "rivers": (119,181,254),       # Bleu pour les rivières
    "text": (0, 0, 0),              # Noir pour le texte
    "control": (0, 0, 0),           # Noir pour le contrôle par défaut
    "background": (245, 245, 220),  # Beige pour le fond
    "units": {"Marquise de Chat": (255, 165, 0), "Alliance": (0, 255, 0)},
    "buildings": {"default": (128, 128, 128)},
    "panel_bg": (200, 200, 200)    # Gris clair pour les panneaux
}

SYMBOL_COLORS = {
    "Renard": (255, 0, 0),    # Rouge pour les renards
    "Lapin":  (255, 255, 0),  # Jaune pour les lapins
    "Souris": (255, 165, 0),  # Orange pour les souris
}

# Dimensions
SCALE = 0.7
WIDTH, HEIGHT = config.WIDTH, config.HEIGHT
GAME_WIDTH   = int(WIDTH * SCALE)
GAME_HEIGHT  = int(HEIGHT * SCALE)
PANEL_WIDTH  = WIDTH - GAME_WIDTH
PANEL_HEIGHT = HEIGHT
NODE_RADIUS  = 30
UNIT_RADIUS  = 10
SYMBOL_SIZE  = 12
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
        self.action_history = []

    def draw_board(self):
        self.screen.fill(COLORS["background"])
        # Dessiner la zone de jeu
        pygame.draw.rect(self.screen, COLORS["panel_bg"], (GAME_WIDTH, 0, PANEL_WIDTH, PANEL_HEIGHT))

        nodes, edges, rivers, forests = self.board.get_nodes_and_edges()

        # Scaling
        def scale_pos(pos):
            return (int(pos[0] * SCALE), int(pos[1] * SCALE))

        # Dessiner les forêts en premier (pour qu'elles soient en arrière-plan)
        for forest_id, forest_data in forests.items():
            points = [scale_pos(p) for p in self.board.get_forest_polygon_points(forest_id)]
            if points:
                pygame.draw.polygon(self.screen, COLORS["forests"], points)
                pygame.draw.polygon(self.screen, COLORS["edges"], points, 2)
                forest_center = scale_pos(forest_data["center"])
                text = self.font.render(forest_id, True, COLORS["text"])
                text_rect = text.get_rect(center=forest_center)
                self.screen.blit(text, text_rect)

        # Dessiner les chemins
        for edge in edges:
            pos1 = scale_pos(nodes[edge[0] - 1][1]["pos"])
            pos2 = scale_pos(nodes[edge[1] - 1][1]["pos"])
            pygame.draw.line(self.screen, COLORS["edges"], pos1, pos2, 3)

        # Dessiner la rivière
        for river in rivers:
            pos1 = scale_pos(nodes[river[0] - 1][1]["pos"])
            pos2 = scale_pos(nodes[river[1] - 1][1]["pos"])
            pygame.draw.line(self.screen, COLORS["rivers"], pos1, pos2, 3)

        # Dessiner les clairières et les unités
        for node, data in nodes:
            pos = scale_pos(data["pos"])
            pygame.draw.circle(self.screen, COLORS["nodes"], pos, NODE_RADIUS)
            text = self.font.render(str(node), True, COLORS["text"])
            self.screen.blit(text, (pos[0] - 10, pos[1] - 10))

            control_color = COLORS["control"]
            if data["control"]:
                control_color = COLORS["units"].get(data["control"], COLORS["control"])
            pygame.draw.circle(self.screen, control_color, pos, CONTROL_RADIUS, 3)

            clearing_type = data["type"]
            if clearing_type in SYMBOL_COLORS:
                symbol_pos = (pos[0] + NODE_RADIUS - 10, pos[1] + NODE_RADIUS - 10)
                pygame.draw.circle(self.screen, SYMBOL_COLORS[clearing_type], symbol_pos, SYMBOL_SIZE // 2)

            offset = -20
            for faction, count in data["units"].items():
                faction_color = COLORS["units"].get(faction, (200, 200, 200))
                unit_pos = (pos[0] + offset, pos[1])
                pygame.draw.circle(self.screen, faction_color, unit_pos, UNIT_RADIUS)
                unit_text = self.unit_font.render(str(count), True, COLORS["text"])
                self.screen.blit(unit_text, (unit_pos[0] - 5, unit_pos[1] - 5))
                offset += 15

    def draw_panel(self, player_turn, scores):
        y_offset = 20
        for player, score in scores.items():
            color = COLORS["units"].get(player, COLORS["text"])
            if player == player_turn:
                color = (255, 0, 0)  # Rouge pour le joueur dont c'est le tour
            text = self.font.render(f"{player}: {score} points", True, color)
            self.screen.blit(text, (GAME_WIDTH + 10, y_offset))
            y_offset += 30

        # Historique des actions
        y_offset += 20
        for action in self.action_history[-10:]:
            text = self.font.render(action, True, COLORS["text"])
            self.screen.blit(text, (GAME_WIDTH + 10, y_offset))
            y_offset += 20

    def add_action(self, action):
        self.action_history.append(action)

    def run(self, player_turn, scores):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.draw_board()
            self.draw_panel(player_turn, scores)
            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()
