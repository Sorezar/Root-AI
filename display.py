import pygame
import config
import os
import math

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
SCALE = 1
WIDTH, HEIGHT = config.WIDTH, config.HEIGHT
GAME_WIDTH   = int(WIDTH * SCALE)
GAME_HEIGHT  = int(HEIGHT * SCALE)
PANEL_WIDTH  = WIDTH - config.BOARD_WIDTH
PANEL_HEIGHT = HEIGHT
NODE_RADIUS  = 30
UNIT_RADIUS  = 10
SYMBOL_SIZE  = 12
CONTROL_RADIUS = NODE_RADIUS
BUILDING_RADIUS = 15
BOARD_OFFSET_X = 10  # Offset pour décaler le plateau
BOARD_OFFSET_Y = 120 # Offset pour descendre le plateau

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
        
        # Charger les images
        self.item_images = {
            item: pygame.image.load(os.path.join("sprites", "items", f"{item}.png"))
            for item in items.get_items()
        }
        
        # Charger les images des jetons
        self.token_images = {}
        token_path = os.path.join("sprites", "tokens")
        for filename in os.listdir(token_path):
            if filename.endswith(".png"):
                token_name = os.path.splitext(filename)[0]
                self.token_images[token_name] = pygame.image.load(os.path.join(token_path, filename))
        
        self.card_images = {}
        self._load_card_images()
        
        # Bouton pour finir le tour
        self.button_pass = pygame.Rect(WIDTH - 200, HEIGHT - 80, 100, 60)
        self.action_buttons = []

    def _load_card_images(self):
        card_dir = os.path.join("sprites", "cards", "base_deck")
        if not os.path.exists(card_dir):
            print(f"Le répertoire {card_dir} est introuvable.")
            return

        for card_file in os.listdir(card_dir):
            if card_file.endswith(".png"):
                card_id = int(os.path.splitext(card_file)[0])
                image_path = os.path.join(card_dir, card_file)
                self.card_images[card_id] = pygame.image.load(image_path)

    def draw_button(self):
        pygame.draw.rect(self.screen, (0, 0, 255), self.button_pass)
        text = self.button_font.render(">", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.button_pass.center)
        self.screen.blit(text, text_rect)

    def is_button_clicked(self, pos):
        return self.button_pass.collidepoint(pos)
    
    def draw_actions(self):
        x_offset = WIDTH - 400
        y_offset = HEIGHT - 80
        button_width = 180
        button_height = 40
        self.action_buttons = []
        actions = self.lobby.get_player(self.lobby.current_player).faction.actions

        for action in actions:
            button_pass = pygame.Rect(x_offset, y_offset, button_width, button_height)
            pygame.draw.rect(self.screen, (0, 128, 0), button_pass)
            text = self.font.render(action, True, (255, 255, 255))
            text_rect = text.get_rect(center=button_pass.center)
            self.screen.blit(text, text_rect)
            self.action_buttons.append((button_pass, action))
            y_offset -= button_height + 10

    def is_action_button_clicked(self, pos):
        for button_pass, action in self.action_buttons:
            if button_pass.collidepoint(pos):
                return action
        return None
    
    def draw_wavy_line(self, start_pos, end_pos, amplitude=6, frequency=2, color=COLORS["rivers"], width=10):
        x1, y1 = start_pos
        x2, y2 = end_pos
        length = math.hypot(x2 - x1, y2 - y1)
        angle = math.atan2(y2 - y1, x2 - x1)
        segments = int(length / frequency)
        
        points = []
        for i in range(segments + 1):
            t = i / segments
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            offset = amplitude * math.sin(2 * math.pi * frequency * t)
            offset_x = offset * math.cos(angle + math.pi / 2)
            offset_y = offset * math.sin(angle + math.pi / 2)
            points.append((x + offset_x, y + offset_y))
        
        pygame.draw.lines(self.screen, color, False, points, width)

    def draw_board(self):
        
        # Background
        self.screen.fill(COLORS["background"])
        
        # Dessiner la zone de jeu
        pygame.draw.rect(self.screen, COLORS["panel_bg"], (GAME_WIDTH, 0, PANEL_WIDTH, PANEL_HEIGHT))
        
        # Dessiner le cadre noir autour de la zone de plateau
        pygame.draw.rect(self.screen, (0, 0, 0), (BOARD_OFFSET_X, BOARD_OFFSET_Y, config.BOARD_WIDTH, config.BOARD_HEIGHT), 5)

        # Récupérer les noeuds, arêtes, rivières et forêts
        nodes, edges, rivers, forests = self.board.get_nodes_and_edges()

        # Scaling
        def scale_pos(pos):
            return (int(pos[0] * SCALE + BOARD_OFFSET_X), int(pos[1] * SCALE + BOARD_OFFSET_Y))

        # Dessiner les forêts en premier (pour qu'elles soient en arrière-plan)
        for forest_id, forest_data in forests.items():
            points = [scale_pos(p) for p in self.board.get_forest_polygon_points(forest_id)]
            if points:
                pygame.draw.polygon(self.screen, COLORS["forests"], points)
                pygame.draw.polygon(self.screen, COLORS["edges"], points, 2)
                forest_center = scale_pos(forest_data["center"])

        # Dessiner les chemins
        for edge in edges:
            pos1 = scale_pos(nodes[edge[0] - 1][1]["pos"])
            pos2 = scale_pos(nodes[edge[1] - 1][1]["pos"])
            pygame.draw.line(self.screen, COLORS["edges"], pos1, pos2, 3)

        # Dessiner la rivière
        for river in rivers:
            pos1 = scale_pos(nodes[river[0] - 1][1]["pos"])
            pos2 = scale_pos(nodes[river[1] - 1][1]["pos"])
            self.draw_wavy_line(pos1, pos2)

        # Dessiner les clairières et les unités
        for node, data in nodes:
            
            # Clairière
            pos = scale_pos(data["pos"])
            pygame.draw.circle(self.screen, COLORS["nodes"], pos, NODE_RADIUS)

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
            
            # Jetons
            token_size = 20
            token_offset_x = -24
            token_offset_y = -NODE_RADIUS - slot_size - 14  # Positionner les jetons au-dessus des slots
            for token in data["tokens"]:
                token_type = token["type"]
                if token_type in self.token_images:
                    token_image = pygame.transform.scale(self.token_images[token_type], (token_size, token_size))
                    self.screen.blit(token_image, (pos[0] + token_offset_x, pos[1] + token_offset_y))
                    token_offset_x += token_size + 5  # Déplacer horizontalement pour le prochain jeton

                    
        # Dessiner les slots pour les items en haut de la carte
        slot_size = 40
        x_offset = 10
        y_offset = 10
        items_list = self.items.get_items()


        item_count = 0
        for item, count in items_list.items():
            for _ in range(count):
                slot_pos = (x_offset + (item_count // 2) * (slot_size + 10), y_offset + (item_count % 2) * (slot_size + 10))
                pygame.draw.rect(self.screen, COLORS["slots"], (*slot_pos, slot_size, slot_size))
                pygame.draw.rect(self.screen, COLORS["slots_borders"], (*slot_pos, slot_size, slot_size), 1)
                item_image = pygame.transform.scale(self.item_images[item], (slot_size, slot_size))
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
            self.screen.blit(text, (config.BOARD_WIDTH + 30, y_offset))
            if player.id == self.lobby.current_player :
                arrow = self.font.render("->", True, (255, 0, 0))
                self.screen.blit(arrow, (config.BOARD_WIDTH + 10, y_offset))
            y_offset += 30

            # Afficher les cartes du joueur
            x_offset = config.BOARD_WIDTH + 30
            for card in player.cards:
                card_image = self.card_images.get(card['id'])
                if card_image:
                    card_image = pygame.transform.scale(card_image, (card_width, card_height))
                    self.screen.blit(card_image, (x_offset, y_offset))
                    x_offset += card_width + 5
            y_offset += card_height + 10

        # Historique des actions
        y_offset += 20
        for action in self.action_history[-10:]:
            text = self.font.render(action, True, COLORS["text"])
            self.screen.blit(text, (config.BOARD_WIDTH + 10, y_offset))
            y_offset += 20

    def draw_cards(self, player):
        card_width = 220
        card_height = 300
        x_offset = 10
        y_offset = HEIGHT - card_height - 10

        for card in player.cards:
            card_image = self.card_images.get(card['id'])
            if card_image:
                card_image = pygame.transform.scale(card_image, (card_width, card_height))
                self.screen.blit(card_image, (x_offset, y_offset))
            x_offset += card_width + 10

    def add_action(self, action):
        self.action_history.append(action)
        
    def ask_for_clearing(self, valid_clearings):
        selected_clearing = None
        circle_radius = 20
        growing = True
        animation_speed = 0.5  # Vitesse de changement du rayon du cercle

        while selected_clearing not in valid_clearings:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    for clearing in valid_clearings:
                        clearing_pos = self.board.graph.nodes[clearing]["pos"]
                        scaled_pos = (int(clearing_pos[0] * SCALE + BOARD_OFFSET_X), int(clearing_pos[1] * SCALE + BOARD_OFFSET_Y))
                        if pygame.Rect(scaled_pos[0] - NODE_RADIUS, scaled_pos[1] - NODE_RADIUS, NODE_RADIUS * 2, NODE_RADIUS * 2).collidepoint(pos):
                            selected_clearing = clearing
                            break

            # Animation du cercle
            if growing:
                circle_radius += animation_speed
                if circle_radius >= 30:
                    growing = False
            else:
                circle_radius -= animation_speed
                if circle_radius <= 20:
                    growing = True

            # Dessiner uniquement ce qui est nécessaire
            self.draw()

            # Dessiner les cercles animés
            for clearing in valid_clearings:
                clearing_pos = self.board.graph.nodes[clearing]["pos"]
                scaled_pos = (int(clearing_pos[0] * SCALE + BOARD_OFFSET_X), int(clearing_pos[1] * SCALE + BOARD_OFFSET_Y))
                pygame.draw.circle(self.screen, (255, 0, 0), scaled_pos, int(circle_radius), 2)

            # Rafraîchir l'écran
            pygame.display.flip()
            self.clock.tick(60)

        return selected_clearing

    def draw(self):
        self.draw_board()
        self.draw_panel()
        self.draw_button()
        self.draw_actions()
        current_player = self.lobby.get_player(self.lobby.current_player)
        self.draw_cards(current_player)
