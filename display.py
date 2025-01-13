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
    "units": 
    {
        0 : (255, 165, 0),
        1 : (0,0,255),
        2 : (0, 255, 0)
    },
    "text_units": 
    {
        0 : (0, 0, 0),
        1 : (255, 255, 255),
        2 : (0, 0, 0)
    },
    "slots" : (230, 230, 230),
    "slots_borders" :(139, 69, 19)
}

# Dimensions
SCALE = 1
WIDTH, HEIGHT = config.WIDTH, config.HEIGHT
GAME_WIDTH   = config.BOARD_WIDTH
GAME_HEIGHT  = config.BOARD_HEIGHT
PANEL_WIDTH  = config.PANEL_WIDTH
PANEL_HEIGHT = config.PANEL_HEIGHT
ACTIONS_WIDTH = config.ACTIONS_WIDTH
ACTIONS_HEIGHT = config.ACTIONS_HEIGHT
NODE_RADIUS  = 50
UNIT_RADIUS  = 12
SYMBOL_SIZE  = 25
CONTROL_RADIUS = NODE_RADIUS
BOARD_OFFSET_X = 10  # Offset pour décaler le plateau
BOARD_OFFSET_Y = 120 # Offset pour descendre le plateau
BUILDING_SIZE = 22
TOKEN_SIZE = 22
ITEM_SIZE = 40

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
        self.unit_selection_font = pygame.font.SysFont(None, 24)
        self.action_history = []
        
        # Charger les sprites des items
        self.item_images = {
            item: pygame.image.load(os.path.join("sprites", "items", f"{item}.png"))
            for item in items.get_items()
        }
        
        # Charger les sprites des jetons
        self.token_images = {}
        token_path = os.path.join("sprites", "tokens")
        for filename in os.listdir(token_path):
            if filename.endswith(".png"):
                token_name = os.path.splitext(filename)[0]
                self.token_images[token_name] = pygame.image.load(os.path.join(token_path, filename))
                
        # Charger les sprites des bâtiments
        self.building_images = {}
        building_path = os.path.join("sprites", "buildings")
        for filename in os.listdir(building_path):
            if filename.endswith(".png"):
                building_name = os.path.splitext(filename)[0]
                self.building_images[building_name] = pygame.image.load(os.path.join(building_path, filename))
        
        # Charger les sprites des cartes
        self.card_images = {}
        card_dir = os.path.join("sprites", "cards", "base_deck")
        for card_file in os.listdir(card_dir):
            if card_file.endswith(".png"):
                card_id = int(os.path.splitext(card_file)[0])
                image_path = os.path.join(card_dir, card_file)
                self.card_images[card_id] = pygame.image.load(image_path)
        
        # Charger les sprites des cartes format réduit
        self.card_images_panel = {}
        card_dir = os.path.join("sprites", "cards", "base_deck", "panels")
        for card_file in os.listdir(card_dir):
            if card_file.endswith(".png"):
                card_id = int(os.path.splitext(card_file)[0])
                image_path = os.path.join(card_dir, card_file)
                self.card_images_panel[card_id] = pygame.image.load(image_path)
                
        # Charger les sprites des types de clairières
        self.clearing_types = {}
        type_path = os.path.join("sprites", "type")
        for filename in os.listdir(type_path):
            if filename.endswith(".png"):
                type_name = os.path.splitext(filename)[0]
                self.clearing_types[type_name] = pygame.image.load(os.path.join(type_path, filename))
        
        # Bouton pour finir le tour
        self.button_pass = pygame.Rect(WIDTH - 200, HEIGHT - 80, 100, 60)
        self.action_buttons = []        

    def draw_button_pass(self):
        pygame.draw.rect(self.screen, (0, 0, 255), self.button_pass)
        text = self.button_font.render(">", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.button_pass.center)
        self.screen.blit(text, text_rect)

    def is_button_pass_clicked(self, pos):
        return self.button_pass.collidepoint(pos)
    
    def draw_actions(self):
        x_offset = WIDTH - ACTIONS_WIDTH + 10
        y_offset = HEIGHT - ACTIONS_HEIGHT + 10
        button_width = 60
        button_height = 60
        self.action_buttons = []
        current_player = self.lobby.get_player(self.lobby.current_player)
        actions = current_player.faction.actions
        available_actions = current_player.get_available_actions(self.board)
        faction_id = current_player.faction.id

        for action in actions:
            button_pass = pygame.Rect(x_offset, y_offset, button_width, button_height)
            action_image_path = os.path.join("sprites", "actions", str(faction_id), f"{action}.png")
            if os.path.exists(action_image_path):
                action_image = pygame.image.load(action_image_path)
                action_image = pygame.transform.scale(action_image, (button_width, button_height))
                self.screen.blit(action_image, (x_offset, y_offset))
            else:
                pygame.draw.rect(self.screen, (0, 128, 0), button_pass)
                text = self.font.render(action, True, (255, 255, 255))
                text_rect = text.get_rect(center=button_pass.center)
                self.screen.blit(text, text_rect)
            
            if action not in available_actions:
                overlay = pygame.Surface((button_width, button_height))
                overlay.set_alpha(128)  
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (x_offset, y_offset))

            self.action_buttons.append((button_pass, action))
            y_offset += button_height + 10

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

    def draw_items(self):
        x_offset = 10
        y_offset = 10
        items_list = self.items.get_items()

        item_count = 0
        for item, count in items_list.items():
            for _ in range(count):
                slot_pos = (x_offset + (item_count // 2) * (ITEM_SIZE + 10), y_offset + (item_count % 2) * (ITEM_SIZE + 10))
                pygame.draw.rect(self.screen, COLORS["slots"], (*slot_pos, ITEM_SIZE, ITEM_SIZE))
                pygame.draw.rect(self.screen, COLORS["slots_borders"], (*slot_pos, ITEM_SIZE, ITEM_SIZE), 1)
                item_image = pygame.transform.scale(self.item_images[item], (ITEM_SIZE, ITEM_SIZE))
                self.screen.blit(item_image, slot_pos)
                item_count += 1

    def draw_board(self):
        
        # Background
        self.screen.fill(COLORS["background"])
        
        # Dessiner la zone de jeu
        pygame.draw.rect(self.screen, COLORS["panel_bg"], (config.BOARD_WIDTH + BOARD_OFFSET_X, 0, GAME_WIDTH, PANEL_HEIGHT))
        
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
            clearing_type_image = pygame.transform.scale(self.clearing_types[clearing_type], (SYMBOL_SIZE, SYMBOL_SIZE))
            clearing_type_pos = (pos[0] + NODE_RADIUS - 20, pos[1] + NODE_RADIUS - 20)
            self.screen.blit(clearing_type_image, clearing_type_pos)

            # Dessiner les bâtiments
            
            for i, building in enumerate(data["buildings"]):
                building_type = building["type"]
                owner = building["owner"]
                if building_type in self.building_images:
                    building_image = pygame.transform.scale(self.building_images[building_type], (BUILDING_SIZE, BUILDING_SIZE))
                    building_pos = (pos[0] - (data["slots"] * (BUILDING_SIZE + 5)) // 2 + i * (BUILDING_SIZE + 5), pos[1] - (NODE_RADIUS // 2) - BUILDING_SIZE + 10)
                    self.screen.blit(building_image, building_pos)

            # Emplacements libres
            for i in range(len(data["buildings"]), data["slots"]):
                slot_pos = (pos[0] - (data["slots"] * (BUILDING_SIZE + 5)) // 2 + i * (BUILDING_SIZE + 5), pos[1] - (NODE_RADIUS // 2) - BUILDING_SIZE + 10)
                pygame.draw.rect(self.screen, COLORS["slots"], (*slot_pos, BUILDING_SIZE, BUILDING_SIZE))
                pygame.draw.rect(self.screen, COLORS["slots_borders"], (*slot_pos, BUILDING_SIZE, BUILDING_SIZE), 1)

            # Unités
            offset = -20
            for faction, count in data["units"].items():
                if count > 0:
                    faction_color = COLORS["units"].get(faction)
                    unit_pos  = (pos[0] + offset, pos[1] + (NODE_RADIUS // 3) )
                    unit_text = self.unit_font.render(str(count), True, COLORS["text_units"].get(faction))
                    pygame.draw.circle(self.screen, faction_color, unit_pos, UNIT_RADIUS)
                    self.screen.blit(unit_text, (unit_pos[0] - 5, unit_pos[1] - 5))
                    offset += 15
            
            # Jetons
            token_offset_y = (-NODE_RADIUS // 2) - BUILDING_SIZE - 10
            tokens_per_row = 5
            num_tokens = len(data["tokens"])
            rows = (num_tokens + tokens_per_row - 1) // tokens_per_row

            for row in range(rows):
                start_index = row * tokens_per_row
                end_index = min(start_index + tokens_per_row, num_tokens)
                row_tokens = data["tokens"][start_index:end_index]
                total_width = len(row_tokens) * TOKEN_SIZE + (len(row_tokens) - 1) * 5
                start_x = pos[0] - total_width // 2
                token_pos_y = pos[1] + token_offset_y - row * (TOKEN_SIZE + 5)

                for i, token in enumerate(row_tokens):
                    token_type = token["type"]
                    if token_type in self.token_images:
                        token_image = pygame.transform.scale(self.token_images[token_type], (TOKEN_SIZE, TOKEN_SIZE))
                        token_pos_x = start_x + i * (TOKEN_SIZE + 5)
                        self.screen.blit(token_image, (token_pos_x, token_pos_y))

    def draw_panel(self):
        y_offset = 20
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
                card_image_panel = self.card_images_panel.get(card['id'])
                if card_image_panel:
                    card_image_panel = pygame.transform.scale(card_image_panel, (card_width, card_height))
                    self.screen.blit(card_image_panel, (x_offset, y_offset))
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
        circle_radius = NODE_RADIUS - 10
        growing = True
        animation_speed = 0.4 # Vitesse de changement du rayon du cercle

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
                if circle_radius >= NODE_RADIUS:
                    growing = False
            else:
                circle_radius -= animation_speed
                if circle_radius <= NODE_RADIUS - 10:
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

    def draw_units_selection(self, units_to_move, max_units, pos):

        x, y = pos
        button_width, button_height = 30, 30

        # Bouton -
        self.button_minus = pygame.Rect(x - button_width *1.5, y, button_width, button_height)
        pygame.draw.rect(self.screen, (220, 220, 220), self.button_minus)
        minus_text = self.unit_selection_font.render("-", True, COLORS["text"])
        minus_text_rect = minus_text.get_rect(center=self.button_minus.center)
        self.screen.blit(minus_text, minus_text_rect)

        # Nombre d'unités
        units_text_rect = pygame.Rect(x - button_width *0.75 , y, button_width * 1.5, button_height)
        pygame.draw.rect(self.screen, (220, 220, 220), units_text_rect)
        units_text = self.unit_selection_font.render(f"{units_to_move}/{max_units}", True, COLORS["text"])
        units_text_center = units_text.get_rect(center=units_text_rect.center)
        self.screen.blit(units_text, units_text_center)

        # Bouton +
        self.button_plus = pygame.Rect(x + button_width * 0.5, y, button_width, button_height)
        pygame.draw.rect(self.screen, (220, 220, 220), self.button_plus)
        plus_text = self.unit_selection_font.render("+", True, COLORS["text"])
        plus_text_rect = plus_text.get_rect(center=self.button_plus.center)
        self.screen.blit(plus_text, plus_text_rect)

        # Bouton OK
        self.button_confirm = pygame.Rect(x - button_width // 2, y + button_height, button_width, button_height)
        pygame.draw.rect(self.screen, (220, 220, 220), self.button_confirm)
        confirm_text = self.unit_selection_font.render("OK", True, COLORS["text"])
        confirm_text_rect = confirm_text.get_rect(center=self.button_confirm.center)
        self.screen.blit(confirm_text, confirm_text_rect)

    def is_button_minus_clicked(self, pos):
        return self.button_minus.collidepoint(pos)

    def is_button_plus_clicked(self, pos):
        return self.button_plus.collidepoint(pos)

    def is_button_confirm_clicked(self, pos):
        return self.button_confirm.collidepoint(pos)    

    def ask_for_units_to_move(self, max_units, pos):
        units_to_move = 1
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.is_button_minus_clicked(event.pos):
                        units_to_move = max(1, units_to_move - 1)
                    elif self.is_button_plus_clicked(event.pos):
                        units_to_move = min(max_units, units_to_move + 1)
                    elif self.is_button_confirm_clicked(event.pos):
                        return units_to_move

            self.draw()
            self.draw_units_selection(units_to_move, max_units, pos)
            
            pygame.display.flip()
            self.clock.tick(60)
            
    def draw(self):
        self.draw_board()
        self.draw_panel()
        self.draw_items()
        self.draw_button_pass()
        self.draw_actions()
        current_player = self.lobby.get_player(self.lobby.current_player)
        self.draw_cards(current_player)
