import pygame
import config
import os

COLORS = {
    "forests": (34, 139, 34),       # Vert forêt
    "nodes": (255, 255, 255),       # Blanc pour les clairières
    "edges": (0, 0, 0),             # Noir pour les connexions
    "rivers": (119,181,254),        # Bleu pour les rivières
    "text": (0, 0, 0),              # Noir pour le texte
    "control": (0, 0, 0),           # Noir pour le contrôle par défaut
    "background": (245, 245, 220),  # Beige pour le fond
    "panel_bg": (200, 200, 200),    # Gris clair pour les panneaux
    "units": {
        0 : (255, 165, 0),
        1 : (0,0,255),
        2 : (0, 255, 0)
        },
    "slots" : (169, 169, 169),
    "slots_borders" :(139, 69, 19),
    "ruins" : (245, 245, 220),
    "buildings": {"default": (128, 128, 128)}
}

SYMBOL_COLORS = {
    "fox": (255, 0, 0),       # Rouge pour les renards
    "rabbit":  (255, 255, 0), # Jaune pour les lapins
    "mouse": (255, 165, 0),   # Orange pour les souris
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
BOARD_OFFSET_Y = 70 # Offset pour descendre le plateau

class RootDisplay:
    def __init__(self, board, lobby, items):
        self.board = board
        self.lobby = lobby
        self.items = items
        pygame.init()
        pygame.display.set_caption("Root")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), config.get_screen_mode())
        self.clock  = pygame.time.Clock()
        self.font   = pygame.font.SysFont(None, 24)
        self.unit_font = pygame.font.SysFont(None, 18)
        self.button_font = pygame.font.SysFont(None, 36)
        self.action_history = []
        
        # Bouton pour finir le tour
        self.button_rect = pygame.Rect(WIDTH - 200, HEIGHT - 80, 100, 60)

    def draw_button(self):
        pygame.draw.rect(self.screen, (0, 0, 255), self.button_rect)
        text = self.button_font.render("Passer le tour", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.button_rect.center)
        self.screen.blit(text, text_rect)

    def is_button_clicked(self, pos):
        return self.button_rect.collidepoint(pos)

    def draw_board(self):
        
        # Background
        self.screen.fill(COLORS["background"])
        
        # Dessiner la zone de jeu
        pygame.draw.rect(self.screen, COLORS["panel_bg"], (GAME_WIDTH, 0, PANEL_WIDTH, PANEL_HEIGHT))

        # Récupérer les noeuds, arêtes, rivières et forêts
        nodes, edges, rivers, forests = self.board.get_nodes_and_edges()

        # Scaling
        def scale_pos(pos):
            return (int(pos[0] * SCALE), int(pos[1] * SCALE + BOARD_OFFSET_Y))

        # Dessiner les forêts en premier (pour qu'elles soient en arrière-plan)
        for forest_id, forest_data in forests.items():
            points = [scale_pos(p) for p in self.board.get_forest_polygon_points(forest_id)]
            if points:
                pygame.draw.polygon(self.screen, COLORS["forests"], points)
                pygame.draw.polygon(self.screen, COLORS["edges"], points, 2)
                forest_center = scale_pos(forest_data["center"])
                #text = self.font.render(forest_id, True, COLORS["text"])
                #text_rect = text.get_rect(center=forest_center)
                #self.screen.blit(text, text_rect)

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
            
            # Clairière
            pos = scale_pos(data["pos"])
            pygame.draw.circle(self.screen, COLORS["nodes"], pos, NODE_RADIUS)
            #text = self.font.render(str(node), True, COLORS["text"])
            #self.screen.blit(text, (pos[0] - 10, pos[1] - 10))

            # Contrôle
            control_color = COLORS["control"]
            if data["control"] != None:
                control_color = COLORS["units"].get(data["control"], COLORS["control"])
            pygame.draw.circle(self.screen, control_color, pos, CONTROL_RADIUS, 3)

            # Type de clairière
            clearing_type = data["type"]
            if clearing_type in SYMBOL_COLORS:
                symbol_pos = (pos[0] + NODE_RADIUS - 10, pos[1] + NODE_RADIUS - 10)
                pygame.draw.circle(self.screen, SYMBOL_COLORS[clearing_type], symbol_pos, SYMBOL_SIZE // 2)

            # Emplacements libres et ruines
            slot_size = 12
            slot_offset = 15
            for i in range(data["slots"]):
                slot_color = COLORS["slots"] if i < data["ruins"] else COLORS["ruins"]
                slot_pos = (pos[0] - (data["slots"] * (slot_size + 5)) // 2 + i * (slot_size + 5), pos[1] - NODE_RADIUS - slot_size + 10)
                pygame.draw.rect(self.screen, slot_color, (*slot_pos, slot_size, slot_size))
                pygame.draw.rect(self.screen, COLORS["slots_borders"], (*slot_pos, slot_size, slot_size), 1)

            # Unités
            offset = -20
            for faction, count in data["units"].items():
                faction_color = COLORS["units"].get(faction, (200, 200, 200))
                unit_pos = (pos[0] + offset, pos[1])
                pygame.draw.circle(self.screen, faction_color, unit_pos, UNIT_RADIUS)
                unit_text = self.unit_font.render(str(count), True, COLORS["text"])
                self.screen.blit(unit_text, (unit_pos[0] - 5, unit_pos[1] - 5))
                offset += 15
                
        # Dessiner les slots pour les items en haut de la carte
        slot_size = 40
        x_offset = 10
        y_offset = 10
        items_list = self.items.get_items()
        item_images = {item: pygame.image.load(os.path.join("sprites", "items", f"{item}.png")) for item in items_list}

        item_count = 0
        for item, count in items_list.items():
            for _ in range(count):
                slot_pos = (x_offset + (item_count // 2) * (slot_size + 10), y_offset + (item_count % 2) * (slot_size + 10))
                pygame.draw.rect(self.screen, COLORS["slots"], (*slot_pos, slot_size, slot_size))
                pygame.draw.rect(self.screen, COLORS["slots_borders"], (*slot_pos, slot_size, slot_size), 1)
                item_image = pygame.transform.scale(item_images[item], (slot_size, slot_size))
                self.screen.blit(item_image, slot_pos)
                item_count += 1

    def draw_panel(self):
        y_offset = 20
        arrow_offset = 10
        card_width = 100
        card_height = 136
        
        for player in self.lobby.players:
            color = COLORS["units"].get(player.faction.id, COLORS["text"])
            text = self.font.render(f"{player.name}: {player.points} points", True, color)
            self.screen.blit(text, (GAME_WIDTH + 30, y_offset))
            if player.id == self.lobby.current_player :
                arrow = self.font.render("->", True, (255, 0, 0))
                self.screen.blit(arrow, (GAME_WIDTH + 10, y_offset))
            y_offset += 30

            # Afficher les cartes du joueur
            x_offset = GAME_WIDTH + 30
            for card in player.cards:
                card_image_path = os.path.join("sprites", "cards", f"{card['id']}.png")
                card_image = pygame.image.load(card_image_path)
                card_image = pygame.transform.scale(card_image, (card_width, card_height))
                self.screen.blit(card_image, (x_offset, y_offset))
                x_offset += card_width + 5
            y_offset += card_height + 10

        # Historique des actions
        y_offset += 20
        for action in self.action_history[-10:]:
            text = self.font.render(action, True, COLORS["text"])
            self.screen.blit(text, (GAME_WIDTH + 10, y_offset))
            y_offset += 20

    def draw_cards(self, player):
        card_width = 250
        card_height = 341
        x_offset = 10
        y_offset = HEIGHT - card_height - 10

        for card in player.cards:
            card_image_path = os.path.join("sprites", "cards", f"{card['id']}.png")
            card_image = pygame.image.load(card_image_path)
            card_image = pygame.transform.scale(card_image, (card_width, card_height))
            self.screen.blit(card_image, (x_offset, y_offset))
            x_offset += card_width + 10

    def add_action(self, action):
        self.action_history.append(action)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.is_button_clicked(event.pos):
                        self.lobby.current_player = (self.lobby.current_player + 1) % len(self.lobby.players)
            self.draw_board()
            self.draw_panel()
            self.draw_button()
            for player in self.lobby.players:
                self.draw_cards(player)
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
