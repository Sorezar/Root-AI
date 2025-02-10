import pygame
import config
import os
import math

class RootDisplay:
    def __init__(self, board, lobby, items):
        pygame.init()
        pygame.display.set_caption("Root")
        self.board  = board
        self.lobby  = lobby
        self.items  = items
        self.screen = pygame.display.set_mode([config.WIDTH, config.HEIGHT])
        self.clock  = pygame.time.Clock()
        self.font   = pygame.font.SysFont(None, 24)
        self.unit_font   = pygame.font.SysFont(None, 18)
        self.button_font = pygame.font.SysFont(None, 36)
        self.unit_selection_font = pygame.font.SysFont(None, 24)
        self.action_history = []
        self.battle_results = {}
        self.show_battle_results = False
        
        self.icon_images           = self.preload_images("sprites/icons", (config.ICON_SIZE, config.ICON_SIZE))
        self.item_images           = self.preload_images("sprites/items", (config.ITEM_SIZE, config.ITEM_SIZE))
        self.token_images          = self.preload_images("sprites/tokens", (config.TOKEN_SIZE, config.TOKEN_SIZE))
        self.building_images       = self.preload_images("sprites/buildings", (config.BUILDING_SIZE, config.BUILDING_SIZE))
        self.card_images           = self.preload_images("sprites/cards/base_deck", (config.CARDS_WIDTH, config.CARDS_HEIGHT))
        self.card_images_players   = self.preload_images("sprites/cards/base_deck/panels", (config.CARDS_PLAYERS_WIDTH, config.CARDS_PLAYERS_HEIGHT))
        self.card_images_crafted_4 = self.preload_images("sprites/cards/base_deck/crafted_4", (config.CRAFTED_CARDS_WIDTH_4, config.CRAFTED_CARDS_HEIGHT_4))
        self.card_images_crafted_6 = self.preload_images("sprites/cards/base_deck/crafted_6", (config.CRAFTED_CARDS_WIDTH_6, config.CRAFTED_CARDS_HEIGHT_6))
        self.clearing_types        = self.preload_images("sprites/type", (config.SYMBOL_SIZE, config.SYMBOL_SIZE))
        self.action_images         = {}
        for faction_id in range(len(os.listdir("sprites/actions"))):
            faction_folder = os.path.join("sprites/actions", str(faction_id))
            self.action_images[faction_id] = self.preload_images(faction_folder, (60, 60))
        
        self.clock.tick(60)

    def preload_images(self, folder_path, size):
        images = {}
        if not os.path.exists(folder_path):
            return images

        for filename in os.listdir(folder_path):
            if filename.endswith(".png"):
                image_name = os.path.splitext(filename)[0]
                image_path = os.path.join(folder_path, filename)
                image = pygame.image.load(image_path)
                images[image_name] = pygame.transform.scale(image, size)
        return images

###############################################################################################
##################################### FONCTIONS DE DESSIN #####################################
###############################################################################################
    def draw_ennemy_cards(self, player):
        pass

    def draw_button_pass(self):
        button_width = 0.05 * config.WIDTH - 5
        button_height = 0.05 * config.HEIGHT - 5
        x_offset = int(config.WIDTH * 0.95)
        y_offset = int(config.HEIGHT * 0.95)
        self.button_pass = pygame.Rect(x_offset, y_offset, button_width, button_height)
        pygame.draw.rect(self.screen, (255, 255, 255), self.button_pass)
        pygame.draw.rect(self.screen, (0, 0, 0), self.button_pass, 2)
        text = self.button_font.render(">", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.button_pass.center)
        self.screen.blit(text, text_rect)
    
    def draw_actions(self, faction_id, actions, possible_actions):

        self.action_buttons = []

        num_actions = len(actions)
        rows = (num_actions + 2) // 3
        total_height = rows * config.ACTIONS_SIZE + (rows - 1) * 10
        y_offset_start = config.ACTIONS_ZONE_Y + (config.ACTIONS_ZONE_HEIGHT - total_height) // 2

        total_width = min(num_actions, 3) * config.ACTIONS_SIZE + (min(num_actions, 3) - 1) * 10
        x_offset_start = config.ACTIONS_ZONE_X + (config.ACTIONS_ZONE_WIDTH - total_width) // 2

        for i, action in enumerate(actions):
            row = i // 3
            col = i % 3
            x_offset = x_offset_start + col * (config.ACTIONS_SIZE + 10)
            y_offset = y_offset_start + row * (config.ACTIONS_SIZE + 10)

            button_pass = pygame.Rect(x_offset, y_offset, config.ACTIONS_SIZE, config.ACTIONS_SIZE)
            action_image = self.action_images[faction_id].get(action)
            if action_image:
                self.screen.blit(action_image, (x_offset, y_offset))
            else:
                pygame.draw.rect(self.screen, (0, 128, 0), button_pass)
                text = self.font.render(action, True, (255, 255, 255))
                text_rect = text.get_rect(center=button_pass.center)
                self.screen.blit(text, text_rect)

            if action not in possible_actions:
                overlay = pygame.Surface((config.ACTIONS_SIZE, config.ACTIONS_SIZE))
                overlay.set_alpha(128)
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (x_offset, y_offset))

            self.action_buttons.append((button_pass, action))
    
    def draw_wavy_line(self, start_pos, end_pos, amplitude=7, frequency=2, color=config.COLORS["rivers"], width=10):
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
        items_bg_rect = pygame.Rect(config.ITEMS_ZONE_X, config.ITEMS_ZONE_Y, config.ITEMS_ZONE_WIDTH, config.ITEMS_ZONE_HEIGHT)
        pygame.draw.rect(self.screen, (230, 190, 255), items_bg_rect)

        items_list = self.items.get_items()
        
        x = config.ITEMS_ZONE_X + (config.ITEMS_ZONE_WIDTH  - (6 * (config.ITEM_SIZE + 10))) // 2
        total_height = (2 * (config.ITEM_SIZE + 10)) - 10
        y = config.ITEMS_ZONE_Y + (config.ITEMS_ZONE_HEIGHT - total_height) // 2
        
        item_count = 0
        for item, count in items_list.items():
            for _ in range(count):
                slot_pos = (x + (item_count // 2) * (config.ITEM_SIZE + 10), y + (item_count % 2) * (config.ITEM_SIZE + 10))
                pygame.draw.rect(self.screen, config.COLORS["slots"], (*slot_pos, config.ITEM_SIZE, config.ITEM_SIZE))
                pygame.draw.rect(self.screen, config.COLORS["borders"], (*slot_pos, config.ITEM_SIZE, config.ITEM_SIZE), 1)
                self.screen.blit(self.item_images[item], slot_pos)
                item_count += 1

    def draw_crafted_items(self, player):
        crafted_items_bg_rect = pygame.Rect(config.CRAFTED_ITEMS_ZONE_X, config.CRAFTED_ITEMS_ZONE_Y, config.CRAFTED_ITEMS_ZONE_WIDTH, config.CRAFTED_ITEMS_ZONE_HEIGHT)
        pygame.draw.rect(self.screen, (135, 206, 235), crafted_items_bg_rect)

        items_list = player.items
        
        x = config.CRAFTED_ITEMS_ZONE_X + (config.ITEMS_ZONE_WIDTH  - (6 * (config.ITEM_SIZE + 10))) // 2
        total_height = (2 * (config.ITEM_SIZE + 10)) - 10
        y = config.CRAFTED_ITEMS_ZONE_Y + (config.ITEMS_ZONE_HEIGHT - total_height) // 2
        
        item_count = 0
        for item, count in items_list.items():
            for _ in range(count):
                slot_pos = (x + (item_count // 2) * (config.ITEM_SIZE + 10), y + (item_count % 2) * (config.ITEM_SIZE + 10))
                pygame.draw.rect(self.screen, config.COLORS["slots"], (*slot_pos, config.ITEM_SIZE, config.ITEM_SIZE))
                pygame.draw.rect(self.screen, config.COLORS["borders"], (*slot_pos, config.ITEM_SIZE, config.ITEM_SIZE), 1)
                self.screen.blit(self.item_images[item], slot_pos)
                item_count += 1

    def draw_board(self):
        
        # Dessiner le cadre noir autour de la zone de plateau
        pygame.draw.rect(self.screen, (0, 0, 0), (config.BOARD_X, config.BOARD_Y, config.BOARD_WIDTH, config.BOARD_HEIGHT), 3)

        # Récupérer les noeuds, arêtes, rivières et forêts
        nodes, edges, rivers, forests = self.board.get_nodes_and_edges()

        # Dessiner les forêts 
        for forest_id, forest_data in forests.items():
            points = [p for p in self.board.get_forest_polygon_points(forest_id)]
            if points:
                pygame.draw.polygon(self.screen, config.COLORS["forests"], points)
                pygame.draw.polygon(self.screen, config.COLORS["edges"], points, 2)

        # Dessiner les chemins
        for edge in edges:
            pos1 = nodes[edge[0] - 1][1]["pos"]
            pos2 = nodes[edge[1] - 1][1]["pos"]
            pygame.draw.line(self.screen, config.COLORS["edges"], pos1, pos2, 3)

        # Dessiner la rivière
        for river in rivers:
            pos1 = nodes[river[0] - 1][1]["pos"]
            pos2 = nodes[river[1] - 1][1]["pos"]
            self.draw_wavy_line(pos1, pos2)

        # Dessiner les clairières et les unités
        for node, data in nodes:
            
            # Clairière
            pos = data["pos"]
            pygame.draw.circle(self.screen, config.COLORS["nodes"], pos, config.NODE_RADIUS)

            # Contrôle
            control_color = config.COLORS["control"]
            if data["control"] != None:
                control_color = config.COLORS["units"].get(data["control"], config.COLORS["control"])
            pygame.draw.circle(self.screen, control_color, pos, config.NODE_RADIUS, 3)

            # Type de clairière
            clearing_type = data["type"]
            clearing_type_pos = (pos[0] + config.NODE_RADIUS - 20, pos[1] + config.NODE_RADIUS - 20)
            self.screen.blit(self.clearing_types[clearing_type], clearing_type_pos)

            # Dessiner les bâtiments
            
            for i, building in enumerate(data["buildings"]):
                building_type = building["type"]
                owner = building["owner"]
                if building_type in self.building_images:
                    building_pos = (pos[0] - (data["slots"] * (config.BUILDING_SIZE + 5)) // 2 + i * (config.BUILDING_SIZE + 5), pos[1] - (config.NODE_RADIUS // 2) - config.BUILDING_SIZE + 10)
                    self.screen.blit(self.building_images[building_type], building_pos)

            # Emplacements libres
            for i in range(len(data["buildings"]), data["slots"]):
                slot_pos = (pos[0] - (data["slots"] * (config.BUILDING_SIZE + 5)) // 2 + i * (config.BUILDING_SIZE + 5), pos[1] - (config.NODE_RADIUS // 2) - config.BUILDING_SIZE + 10)
                pygame.draw.rect(self.screen, config.COLORS["slots"], (*slot_pos, config.BUILDING_SIZE, config.BUILDING_SIZE))
                pygame.draw.rect(self.screen, config.COLORS["borders"], (*slot_pos, config.BUILDING_SIZE, config.BUILDING_SIZE), 1)

            # Unités
            offset = -20
            for faction, count in data["units"].items():
                if count > 0:
                    faction_color = config.COLORS["units"].get(faction)
                    unit_pos  = (pos[0] + offset, pos[1] + (config.NODE_RADIUS // 3) )
                    unit_text = self.unit_font.render(str(count), True, config.COLORS["text_units"].get(faction))
                    pygame.draw.circle(self.screen, faction_color, unit_pos, config.UNIT_RADIUS)
                    self.screen.blit(unit_text, (unit_pos[0] - 5, unit_pos[1] - 5))
                    offset += 15
            
            # Jetons
            token_offset_y = (-config.NODE_RADIUS // 2) - config.BUILDING_SIZE - 10
            tokens_per_row = 5
            num_tokens = len(data["tokens"])
            rows = (num_tokens + tokens_per_row - 1) // tokens_per_row

            for row in range(rows):
                start_index = row * tokens_per_row
                end_index = min(start_index + tokens_per_row, num_tokens)
                row_tokens = data["tokens"][start_index:end_index]
                total_width = len(row_tokens) * config.TOKEN_SIZE + (len(row_tokens) - 1) * 5
                start_x = pos[0] - total_width // 2
                token_pos_y = pos[1] + token_offset_y - row * (config.TOKEN_SIZE + 5)

                for i, token in enumerate(row_tokens):
                    token_type = token["type"]
                    if token_type in self.token_images:
                        token_pos_x = start_x + i * (config.TOKEN_SIZE + 5)
                        self.screen.blit(self.token_images[token_type], (token_pos_x, token_pos_y))
                        
        # Dessiner les unités dans les forêts
        for forest_id, forest_data in forests.items():
            for faction_id, unit_count in forest_data.get("units", {}).items():
                if unit_count > 0:
                    pos = forest_data["center"]
                    for i in range(unit_count):
                        pygame.draw.circle(self.screen, config.COLORS["units"].get(faction_id), pos, config.UNIT_RADIUS)

    def draw_players(self):
        num_players = len(self.lobby.players)
        player_width = config.PLAYERS_WIDTH // num_players
        player_height = config.PLAYERS_HEIGHT

        for i, player in enumerate(self.lobby.players):
            x_offset = config.PLAYERS_X + i * player_width
            y_offset = config.PLAYERS_Y

            # Dessiner le background du joueur
            player_bg_rect = pygame.Rect(x_offset, y_offset, player_width, player_height)
            pygame.draw.rect(self.screen, (220, 220, 220), player_bg_rect)

            # Dessiner le cadre autour du joueur
            faction_color = config.COLORS["units"].get(player.faction.id)
            pygame.draw.rect(self.screen, faction_color, player_bg_rect, 2)

            # Afficher le nom du joueur et ses points
            text = self.font.render(f"{player.name}: {player.points} pts", True, faction_color)
            self.screen.blit(text, (x_offset + 25, y_offset + 5))
            if player.id == self.lobby.current_player:
                self.screen.blit(self.font.render("->", True, (0, 0, 0)), (x_offset + 5, y_offset + 5))

            # Afficher les cartes du joueur
            card_x_offset = x_offset + 10
            for card in player.cards:
                card_image_players = self.card_images_players[str(card['id'])]
                if card_image_players:
                    self.screen.blit(card_image_players, (card_x_offset, y_offset + self.font.get_linesize() + 10))
                    card_x_offset += config.CARDS_PLAYERS_WIDTH + 5

            # Afficher les cartes fabriquées avec un background plus clair
            crafted_x_offset = x_offset + 10
            crafted_bg_rect = pygame.Rect(crafted_x_offset - 5, y_offset + player_height - config.CARDS_PLAYERS_HEIGHT - 15, player_width * 0.8, config.CARDS_PLAYERS_HEIGHT + 10)
            pygame.draw.rect(self.screen, (200, 200, 200), crafted_bg_rect)
            for card in player.crafted_cards:
                card_image_players = self.card_images_players[str(card['id'])]
                if card_image_players:
                    self.screen.blit(card_image_players, (crafted_x_offset, y_offset + player_height - config.CARDS_PLAYERS_HEIGHT - 10))
                    crafted_x_offset += config.CARDS_PLAYERS_WIDTH + 5

            # Afficher le cercle avec le nombre d'unités restantes
            unit_circle_pos = (x_offset + player_width - config.UNIT_RADIUS - 10, y_offset + config.UNIT_RADIUS + 10)
            pygame.draw.circle(self.screen, faction_color, unit_circle_pos, config.UNIT_RADIUS)
            units_text = self.font.render(str(player.faction.units), True, (255, 255, 255))
            units_text_rect = units_text.get_rect(center=unit_circle_pos)
            self.screen.blit(units_text, units_text_rect)
            
            # Afficher les items du joueur
            item_x_offset = unit_circle_pos[0] - 40
            item_y_offset = unit_circle_pos[1] + config.UNIT_RADIUS + 5
            
            item_count = 0
            for item, count in player.items.items():
                if count > 0:
                    item_image = pygame.transform.scale(self.item_images.get(item), (20, 20))
                    for _ in range(count):
                        self.screen.blit(item_image, (item_x_offset + (item_count % 2) * (20 + 5), item_y_offset + (item_count // 2) * (20 + 5)))
                        item_count += 1

    def draw_cards(self, player):
 
            num_cards = len(player.cards)
            total_width = num_cards * config.CARDS_WIDTH + (num_cards - 1) * 5
            x_offset = config.CARDS_ZONE_X + (config.CARDS_ZONE_WIDTH - total_width) // 2
            y_offset = config.CARDS_ZONE_Y + (config.CARDS_ZONE_HEIGHT - config.CARDS_HEIGHT) // 2

            for card in player.cards:
                card_image = self.card_images[str(card['id'])]
                if card_image:
                    self.screen.blit(card_image, (x_offset, y_offset))
                    x_offset += config.CARDS_WIDTH + 5

    def draw_units_selection(self, units_to_move, max_units, pos):

        x, y = pos
        button_width, button_height = 30, 30

        # Bouton -
        self.button_minus = pygame.Rect(x - button_width *1.5, y, button_width, button_height)
        pygame.draw.rect(self.screen, (220, 220, 220), self.button_minus)
        minus_text = self.unit_selection_font.render("-", True, config.COLORS["text"])
        minus_text_rect = minus_text.get_rect(center=self.button_minus.center)
        self.screen.blit(minus_text, minus_text_rect)

        # Nombre d'unités
        units_text_rect = pygame.Rect(x - button_width *0.75 , y, button_width * 1.5, button_height)
        pygame.draw.rect(self.screen, (220, 220, 220), units_text_rect)
        units_text = self.unit_selection_font.render(f"{units_to_move}/{max_units}", True, config.COLORS["text"])
        units_text_center = units_text.get_rect(center=units_text_rect.center)
        self.screen.blit(units_text, units_text_center)

        # Bouton +
        self.button_plus = pygame.Rect(x + button_width * 0.5, y, button_width, button_height)
        pygame.draw.rect(self.screen, (220, 220, 220), self.button_plus)
        plus_text = self.unit_selection_font.render("+", True, config.COLORS["text"])
        plus_text_rect = plus_text.get_rect(center=self.button_plus.center)
        self.screen.blit(plus_text, plus_text_rect)

        # Bouton OK
        self.button_confirm = pygame.Rect(x - button_width // 2, y + button_height, button_width, button_height)
        pygame.draw.rect(self.screen, (220, 220, 220), self.button_confirm)
        confirm_text = self.unit_selection_font.render("OK", True, config.COLORS["text"])
        confirm_text_rect = confirm_text.get_rect(center=self.button_confirm.center)
        self.screen.blit(confirm_text, confirm_text_rect)

    def draw_decree(self, current_player):
        decree = current_player.faction.decrees
        actions = ["recruit", "move", "battle", "build"]
        action_labels = ["Recruit", "Move", "Battle", "Build"]
        column_width = 30
        column_height = 90
        padding = 40       # Augmenter l'espacement entre les colonnes
        label_offset = 10  # Réduire l'espace entre les images et le titre des colonnes
        line_height = 90   # Hauteur des lignes verticales

        # Calculer les offsets pour centrer le décret dans la zone ACTIONS
        total_width = len(actions) * (column_width + padding) - padding
        total_height = column_height + label_offset  # Inclure l'espace pour les labels
        x_offset = config.ACTIONS_ZONE_X + (config.ACTIONS_ZONE_WIDTH - total_width) // 2
        y_offset = config.ACTIONS_ZONE_Y + (config.ACTIONS_ZONE_HEIGHT - total_height) // 2

        for i, action in enumerate(actions):
            # Dessiner le label de l'action
            label_text = self.font.render(action_labels[i], True, config.COLORS["text"])
            label_rect = label_text.get_rect(center=(x_offset + column_width // 2, y_offset - label_offset))
            self.screen.blit(label_text, label_rect)

            # Dessiner les cartes du décret
            for j, color in enumerate(decree[action]):
                sprite_pos = (x_offset, y_offset + j * column_width)
                self.screen.blit(self.clearing_types[color], sprite_pos)

            # Dessiner les lignes verticales entre les colonnes
            if i < len(actions) - 1:
                line_x = x_offset + column_width + padding // 2
                line_y_start = y_offset - label_offset // 2
                line_y_end = line_y_start + line_height
                pygame.draw.line(self.screen, config.COLORS["text"], (line_x, line_y_start), (line_x, line_y_end), 2)

            x_offset += column_width + padding
            
    def draw_message(self, message, duration=2000):
        font = pygame.font.SysFont(None, 48)
        text = font.render(message, True, config.COLORS["text"])
        text_rect = text.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2))
        
        self.draw()  
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        
        pygame.time.delay(duration)

    def draw_battle_results(self):
        attack_clearing = self.battle_results["attack_clearing"]
        attacker_roll = self.battle_results["attacker_roll"]
        defender_roll = self.battle_results["defender_roll"]
        attacker_damage = self.battle_results["attacker_damage"]
        defender_damage = self.battle_results["defender_damage"]

        clearing_pos = self.board.graph.nodes[attack_clearing]["pos"]
        scaled_pos = (int(clearing_pos[0]), int(clearing_pos[1]))

        # Dessiner les résultats des dés
        font = pygame.font.SysFont(None, 24)
        text_color = (255, 0, 0)
        background_color = (255, 255, 255)
        
        attacker_roll_text = font.render(f"Att Dice : {attacker_roll}", True, text_color, background_color)
        defender_roll_text = font.render(f"Def Dice: {defender_roll}", True, text_color, background_color)
        attacker_damage_text = font.render(f"Att Dmg: {attacker_damage}", True, text_color, background_color)
        defender_damage_text = font.render(f"Def Dmg: {defender_damage}", True, text_color, background_color)
        
        self.screen.blit(attacker_roll_text, (scaled_pos[0] - attacker_roll_text.get_width() // 2, scaled_pos[1] - 100))
        self.screen.blit(defender_roll_text, (scaled_pos[0] - defender_roll_text.get_width() // 2, scaled_pos[1] - 70))
        self.screen.blit(attacker_damage_text, (scaled_pos[0] - attacker_damage_text.get_width() // 2, scaled_pos[1] - 40))
        self.screen.blit(defender_damage_text, (scaled_pos[0] - defender_damage_text.get_width() // 2, scaled_pos[1] - 10))

    def draw_history(self):
        # Dessiner le background de l'historique
        history_bg_rect = pygame.Rect(config.HISTORY_X, config.HISTORY_Y, config.HISTORY_WIDTH, config.HISTORY_HEIGHT)
        pygame.draw.rect(self.screen, (220, 220, 220), history_bg_rect)

    def draw_crafted_cards(self, player):
        crafted_cards_bg_rect = pygame.Rect(config.CRAFTED_CARDS_ZONE_X, config.CRAFTED_CARDS_ZONE_Y, config.CRAFTED_CARDS_ZONE_WIDTH, config.CRAFTED_CARDS_ZONE_HEIGHT)
        pygame.draw.rect(self.screen, (255, 215, 0), crafted_cards_bg_rect)
        num_cards = len(player.crafted_cards)
        
        if num_cards > 4:
            card_width = config.CRAFTED_CARDS_WIDTH_6
            card_height = config.CRAFTED_CARDS_HEIGHT_6
        else:
            card_width = config.CRAFTED_CARDS_WIDTH_4
            card_height = config.CRAFTED_CARDS_HEIGHT_4
        
        rows = (num_cards + 1) // 2
        total_height = rows * card_height + (rows - 1) * 10
        y_offset = config.CRAFTED_CARDS_ZONE_Y + (config.CRAFTED_CARDS_ZONE_HEIGHT - total_height) // 2

        for i, card in enumerate(player.crafted_cards):
            row = i // 2
            col = i % 2
            x = config.CRAFTED_CARDS_ZONE_X + (config.CRAFTED_CARDS_ZONE_WIDTH - (2 * (card_width + 10))) // 2 + col * (card_width + 10)
            y = y_offset + row * (card_height + 10)
            if num_cards > 4:
                self.screen.blit(self.card_images_crafted_6[str(card['id'])], (x, y))
            else:
                self.screen.blit(self.card_images_crafted_4[str(card['id'])], (x, y))

    def draw_supporters_and_officers(self, current_player):
        supporters = current_player.faction.supporters
        officers = current_player.faction.officers

        # Dessiner les supporters
        supporter_types = ["fox", "rabbit", "mouse", "bird"]
        icon_size = 25
        padding = 10

        total_width = len(supporter_types) * (icon_size + padding) - padding + icon_size + padding
        x_offset = config.ACTIONS_ZONE_X + (config.ACTIONS_ZONE_WIDTH - total_width) // 2
        y_offset = config.ACTIONS_ZONE_Y + 10

        for i, supporter_type in enumerate(supporter_types):
            icon = self.clearing_types[supporter_type]
            self.screen.blit(icon, (x_offset + i * (icon_size + padding), y_offset))
            count_text = self.font.render(str(supporters.get(supporter_type, 0)), True, config.COLORS["text"])
            self.screen.blit(count_text, (x_offset + i * (icon_size + padding) + icon_size // 2 - count_text.get_width() // 2, y_offset + icon_size + 5))

        # Dessiner la ligne verticale
        line_x = x_offset + total_width + padding
        pygame.draw.line(self.screen, config.COLORS["text"], (line_x, y_offset), (line_x, y_offset + icon_size + 30), 2)

        # Dessiner les officiers
        officer_icon = pygame.transform.scale(self.icon_images["officers"], (icon_size, icon_size))
        officer_count_text = self.font.render(str(officers), True, config.COLORS["text"])
        officer_x_offset = line_x + padding
        officer_y_offset = y_offset

        self.screen.blit(officer_icon, (officer_x_offset, officer_y_offset))
        self.screen.blit(officer_count_text, (officer_x_offset + officer_icon.get_width() // 2 - officer_count_text.get_width() // 2, officer_y_offset + officer_icon.get_height() + 5))

    def draw(self):
        current_player = self.lobby.get_player(self.lobby.current_player)
        self.screen.fill(config.COLORS["background"])
        
        self.draw_players()
        self.draw_items()
        self.draw_history()
        self.draw_board()
        self.draw_cards(current_player)
        self.draw_crafted_cards(current_player)
        self.draw_crafted_items(current_player)
        self.draw_button_pass()
        
        if current_player.faction.id == 1:  # Canopée
            self.draw_decree(current_player)
        elif current_player.faction.id == 2:  # Alliance
            self.draw_supporters_and_officers(current_player)
        if self.show_battle_results:
            self.draw_battle_results()

###############################################################################################
################################### FONCTIONS D'INTERACTION ###################################
###############################################################################################

    def ask_for_players(self, players, pass_available=False):
        selected_player = None
        player_width = config.PLAYERS_WIDTH // len(self.lobby.players)
        player_height = config.PLAYERS_HEIGHT

        while selected_player is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if pass_available and self.is_button_pass_clicked(pos): return "pass"
                    for i, player in enumerate(self.lobby.players):
                        if player in players:
                            x_offset = config.PLAYERS_X + i * player_width
                            y_offset = config.PLAYERS_Y
                            player_rect = pygame.Rect(x_offset, y_offset, player_width, player_height)
                            if player_rect.collidepoint(pos):
                                selected_player = player
                                break

            self.draw()

            # Highlight selectable players
            for i, player in enumerate(self.lobby.players):
                if player in players:
                    x_offset = config.PLAYERS_X + i * player_width
                    y_offset = config.PLAYERS_Y
                    player_rect = pygame.Rect(x_offset, y_offset, player_width, player_height)
                    pygame.draw.rect(self.screen, (255, 0, 0), player_rect, 3)

            pygame.display.flip()

        return selected_player

    def ask_for_clearing(self, valid_clearings, pass_available=False, costs=None):
        selected_clearing = None
        circle_radius = config.NODE_RADIUS - 10
        growing = True
        animation_speed = 0.4

        while selected_clearing not in valid_clearings:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if pass_available and self.is_button_pass_clicked(pos): return "pass"
                    for clearing in valid_clearings:
                        clearing_pos = self.board.graph.nodes[clearing]["pos"]
                        if pygame.Rect(clearing_pos[0] - config.NODE_RADIUS, clearing_pos[1] - config.NODE_RADIUS, config.NODE_RADIUS * 2, config.NODE_RADIUS * 2).collidepoint(pos):
                            selected_clearing = clearing
                            break

            # Animation du cercle
            if growing:
                circle_radius += animation_speed
                if circle_radius >= config.NODE_RADIUS:
                    growing = False
            else:
                circle_radius -= animation_speed
                if circle_radius <= config.NODE_RADIUS - 10:
                    growing = True

            # Dessiner uniquement ce qui est nécessaire
            self.draw()

            # Dessiner les cercles animés
            for clearing in valid_clearings:
                clearing_pos = self.board.graph.nodes[clearing]["pos"]
                pygame.draw.circle(self.screen, (255, 0, 0), clearing_pos, int(circle_radius), 2)

                # Afficher les coûts si disponibles
                if costs:
                    for cost in costs:
                        if cost['clearing'] == clearing:
                            cost_text = f"Cost: {cost['clearing_type_cost']} (Type), {cost['bird_cost']} (Bird)"
                            cost_surface = self.font.render(cost_text, True, (255, 255, 255))
                            cost_rect = cost_surface.get_rect(center=(clearing_pos[0], clearing_pos[1] + config.NODE_RADIUS + 15))
                            self.screen.blit(cost_surface, cost_rect)

            # Rafraîchir l'écran
            pygame.display.flip()

        return selected_clearing

    def ask_for_cards(self, player, criteria=None, values=None, pass_available=False):
        selected_card = None
        num_cards = len(player.cards)
        total_width = num_cards * config.CARDS_WIDTH + (num_cards - 1) * 5
        x_offset = config.CARDS_ZONE_X + (config.CARDS_ZONE_WIDTH - total_width) // 2
        y_offset = config.CARDS_ZONE_Y + (config.CARDS_ZONE_HEIGHT - config.CARDS_HEIGHT) // 2

        while selected_card is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if pass_available and self.is_button_pass_clicked(pos): return "pass"
                    x_offset = config.CARDS_ZONE_X + (config.CARDS_ZONE_WIDTH - total_width) // 2  # Reset x_offset for each click check
                    for card in player.cards:
                        if criteria is None or card.get(criteria) in values:
                            card_pos = (x_offset, y_offset)
                            if pygame.Rect(card_pos[0], card_pos[1], config.CARDS_WIDTH, config.CARDS_HEIGHT).collidepoint(pos):
                                selected_card = card
                                break
                        x_offset += config.CARDS_WIDTH + 5

            # Dessiner uniquement ce qui est nécessaire
            self.draw()

            # Dessiner les cartes en surbrillance
            x_offset = config.CARDS_ZONE_X + (config.CARDS_ZONE_WIDTH - total_width) // 2
            for card in player.cards:
                card_pos = (x_offset, y_offset)
                if criteria is None or card.get(criteria) in values:
                    pygame.draw.rect(self.screen, (255, 0, 0), (card_pos[0], card_pos[1], config.CARDS_WIDTH, config.CARDS_HEIGHT), 3)
                x_offset += config.CARDS_WIDTH + 5
                
            # Rafraîchir l'écran
            pygame.display.flip()

        return selected_card

    def ask_for_crafted_cards(self, player, criteria=None, values=None, pass_available=False):
        selected_card = None
        num_cards = len(player.crafted_cards)
        card_width = config.CRAFTED_CARDS_WIDTH_6 if num_cards > 4 else config.CRAFTED_CARDS_WIDTH_4
        card_height = config.CRAFTED_CARDS_HEIGHT_6 if num_cards > 4 else config.CRAFTED_CARDS_HEIGHT_4

        while selected_card is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if pass_available and self.is_button_pass_clicked(pos): return "pass"
                    x_offset = config.CRAFTED_CARDS_ZONE_X + (config.CRAFTED_CARDS_ZONE_WIDTH - (2 * (card_width + 10))) // 2
                    y_offset = config.CRAFTED_CARDS_ZONE_Y + (config.CRAFTED_CARDS_ZONE_HEIGHT - ((num_cards // 2 + num_cards % 2) * (card_height + 10))) // 2
                    for i, card in enumerate(player.crafted_cards):
                        row = i // 2
                        col = i % 2
                        card_pos = (x_offset + col * (card_width + 10), y_offset + row * (card_height + 10))
                        if criteria is None or card.get(criteria) in values:
                            if pygame.Rect(card_pos[0], card_pos[1], card_width, card_height).collidepoint(pos):
                                selected_card = card
                                break

            # Dessiner uniquement ce qui est nécessaire
            self.draw()

            # Dessiner les cartes en surbrillance
            x_offset = config.CRAFTED_CARDS_ZONE_X + (config.CRAFTED_CARDS_ZONE_WIDTH - (2 * (card_width + 10))) // 2
            y_offset = config.CRAFTED_CARDS_ZONE_Y + (config.CRAFTED_CARDS_ZONE_HEIGHT - ((num_cards // 2 + num_cards % 2) * (card_height + 10))) // 2
            for i, card in enumerate(player.crafted_cards):
                row = i // 2
                col = i % 2
                card_pos = (x_offset + col * (card_width + 10), y_offset + row * (card_height + 10))
                if criteria is None or card.get(criteria) in values:
                    pygame.draw.rect(self.screen, (255, 0, 0), (card_pos[0], card_pos[1], card_width, card_height), 3)

            # Rafraîchir l'écran
            pygame.display.flip()

        return selected_card

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
            
    def ask_for_building_cats(self, pos, wood_costs, max_wood, buildings):
        selected_building = None
        building_types = ["sawmill", "workshop", "recruiter"]
        building_width = 40
        building_height = 40
        padding = 10

        while selected_building is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    click_pos = event.pos
                    for i, building in enumerate(building_types):
                        building_rect = pygame.Rect(pos[0] + i * (building_width + padding), pos[1] - building_height // 2, building_width, building_height)
                        if building_rect.collidepoint(click_pos) and wood_costs[i] <= max_wood and buildings[building] > 0:
                            selected_building = building
                            break

            self.draw()

            # Dessiner les bâtiments et leurs coûts
            for i, (building, cost) in enumerate(zip(building_types, wood_costs)):
                building_rect = pygame.Rect(pos[0] + i * (building_width + padding), pos[1] - building_height // 2, building_width, building_height)
                self.screen.blit(self.building_images[building], building_rect.topleft)

                # Afficher le coût en bois
                cost_text = self.font.render(str(cost), True, config.COLORS["text"])
                self.screen.blit(cost_text, (building_rect.x + building_width // 2 - cost_text.get_width() // 2, building_rect.y + building_height + 5))

                # Appliquer un filtre noirci si le coût en bois est supérieur à max_wood ou si le nombre de bâtiments est épuisé
                if cost > max_wood or buildings[building] <= 0:
                    overlay = pygame.Surface((building_width, building_height))
                    overlay.set_alpha(128)
                    overlay.fill((0, 0, 0))
                    self.screen.blit(overlay, building_rect.topleft)

            # Rafraîchir l'écran
            pygame.display.flip()
            
        return selected_building, wood_costs[building_types.index(selected_building)]
 
    def ask_for_enemy(self, clearing, enemy_factions, pass_available=False):
        selected_faction = None
        icon_size = 40
        padding = 10
        
        clearing_pos = self.board.graph.nodes[clearing]["pos"]
        scaled_pos = (int(clearing_pos[0]), int(clearing_pos[1]))

        while selected_faction is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if pass_available and self.is_button_pass_clicked(pos): return "pass"
                    for i, faction_id in enumerate(enemy_factions):
                        icon_rect = pygame.Rect(scaled_pos[0] - icon_size // 2, scaled_pos[1] - (i + 1) * (icon_size + padding), icon_size, icon_size)
                        if icon_rect.collidepoint(pos):
                            selected_faction = faction_id
                            break

            # Dessiner uniquement ce qui est nécessaire
            self.draw()

            # Dessiner les icônes des factions ennemies
            for i, faction_id in enumerate(enemy_factions):
                icon_rect = pygame.Rect(scaled_pos[0] - icon_size // 2, scaled_pos[1] - (i + 1) * (icon_size + padding), icon_size, icon_size)
                self.screen.blit(self.icon_images[str(faction_id)], icon_rect.topleft)

            # Rafraîchir l'écran
            pygame.display.flip()

        return selected_faction
    
    def ask_what_to_remove(self, clearing, faction_id):
        selected_item = None
        selected_type = None
        item_width = 40
        item_height = 40
        padding = 10

        clearing_pos = self.board.graph.nodes[clearing]["pos"]
        scaled_pos = (int(clearing_pos[0]), int(clearing_pos[1]))

        # Récupérer les bâtiments et jetons du défenseur
        buildings = [b for b in self.board.graph.nodes[clearing]["buildings"] if b["owner"] == faction_id]
        tokens = [t for t in self.board.graph.nodes[clearing]["tokens"] if t["owner"] == faction_id]

        while selected_item is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    click_pos = event.pos
                    x_offset = scaled_pos[0] - (len(buildings) + len(tokens)) * (item_width + padding) // 2
                    for i, item in enumerate(buildings + tokens):
                        item_rect = pygame.Rect(x_offset + i * (item_width + padding), scaled_pos[1] - item_height - 10, item_width, item_height)
                        if item_rect.collidepoint(click_pos):
                            selected_item = item
                            selected_type = "building" if item in buildings else "token"
                            break

            # Dessiner uniquement ce qui est nécessaire
            self.draw()

            # Dessiner les bâtiments et jetons
            x_offset = scaled_pos[0] - (len(buildings) + len(tokens)) * (item_width + padding) // 2
            for i, item in enumerate(buildings + tokens):
                item_rect = pygame.Rect(x_offset + i * (item_width + padding), scaled_pos[1] - item_height - 10, item_width, item_height)
                if "type" in item:
                    if item["type"] in self.building_images:
                        item_image = self.building_images[item["type"]],
                    elif item["type"] in self.token_images:
                        item_image = self.token_images[item["type"]]
                    else:
                        continue
                else:
                    continue
                self.screen.blit(item_image, item_rect.topleft)

            # Rafraîchir l'écran
            pygame.display.flip()

        return selected_item, selected_type

    def ask_for_action_birds(self):
        actions = ["recruit", "move", "battle", "build"]
        action_buttons = []
        button_width = 80
        button_height = 50
        total_width = len(actions) * (button_width + 10) - 10
        x_offset = config.ACTIONS_ZONE_X + (config.ACTIONS_ZONE_WIDTH - total_width) // 2
        y_offset = config.ACTIONS_ZONE_Y + 10

        for action in actions:
            button_rect = pygame.Rect(x_offset, y_offset, button_width, button_height)
            action_buttons.append((button_rect, action))
            x_offset += button_width + 10

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for button_rect, action in action_buttons:
                        if button_rect.collidepoint(event.pos):
                            return action

            # Dessiner uniquement ce qui est nécessaire
            self.draw()

            # Dessiner les boutons d'action
            for button_rect, action in action_buttons:
                pygame.draw.rect(self.screen, (0, 128, 0), button_rect)
                text = self.font.render(action, True, (255, 255, 255))
                text_rect = text.get_rect(center=button_rect.center)
                self.screen.blit(text, text_rect)

            # Rafraîchir l'écran
            pygame.display.flip()
        
    def is_point_in_polygon(self,point, polygon):
        x, y = point
        inside = False
        for i in range(len(polygon)):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i + 1) % len(polygon)]
            if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
                inside = not inside
        return inside

    def ask_for_slip(self, clearings, forests, pass_available=False):
        selected_target = None
        circle_radius = config.NODE_RADIUS - 10
        growing = True
        animation_speed = 0.4

        while selected_target not in clearings and selected_target not in forests:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if pass_available and self.is_button_pass_clicked(pos):
                        return "pass"
                    for clearing in clearings:
                        clearing_pos = self.board.graph.nodes[clearing]["pos"]
                        rect_area = pygame.Rect(
                            clearing_pos[0] - config.NODE_RADIUS,
                            clearing_pos[1] - config.NODE_RADIUS,
                            config.NODE_RADIUS * 2,
                            config.NODE_RADIUS * 2
                        )
                        # Vérifier si on a cliqué sur une clairière
                        if rect_area.collidepoint(pos):
                            selected_target = clearing
                            break

                    # Si aucune clairière n'a été sélectionnée, vérifier les forêts
                    if not selected_target:
                        for forest in forests:
                            polygon_points = list(self.board.get_forest_polygon_points(forest))
                            if self.is_point_in_polygon(pos, polygon_points):
                                selected_target = forest
                                break

            if growing:
                circle_radius += animation_speed
                if circle_radius >= config.NODE_RADIUS:
                    growing = False
            else:
                circle_radius -= animation_speed
                if circle_radius <= config.NODE_RADIUS - 10:
                    growing = True

            self.draw()

            for clearing in clearings:
                p = self.board.graph.nodes[clearing]["pos"]
                pygame.draw.circle(self.screen, (255, 0, 0), p, int(circle_radius), 2)

            line_width = max(1, int(circle_radius - (config.NODE_RADIUS - 5)))
            for forest in forests:
                polygon_points = list(self.board.get_forest_polygon_points(forest))
                pygame.draw.polygon(self.screen, (255, 0, 0), polygon_points, line_width)

            pygame.display.flip()

        return selected_target
        
###############################################################################################
#################################### FONCTIONS D'EVENEMENT ####################################
###############################################################################################

    def is_button_pass_clicked(self, pos):
        return self.button_pass.collidepoint(pos)
    
    def is_button_minus_clicked(self, pos):
        return self.button_minus.collidepoint(pos)

    def is_button_plus_clicked(self, pos):
        return self.button_plus.collidepoint(pos)

    def is_button_confirm_clicked(self, pos):
        return self.button_confirm.collidepoint(pos) 
    
    def is_action_button_clicked(self, pos):
        for button_pass, action in self.action_buttons:
            if button_pass.collidepoint(pos):
                return action
        return None