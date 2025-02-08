from factions.BaseFaction import Base
import pygame
# Under development

class Alliance(Base):
    def __init__ (self):
        super().__init__("Alliance de la forêt", 2)
        self.buildings = {
            "base_fox" : 1,
            "base_rabbit" : 1,
            "base_mouse" : 1
        }
        self.supporters = {
            "fox" : 1,
            "rabbit" : 1,
            "mouse" : 1,
            "bird" : 0
        }
        self.tokens = {
            "sympathy" : 10
        }
        self.units = 10
        self.officers = 0
        self.daylight_actions = ["craft", "mobilize", "train"]
        self.evening_actions = ["move", "battle", "recruit", "organize"]

############################################################################################################
###################################### VERIFICATIONS ACTIONS POSSIBLES #####################################
############################################################################################################

    def is_craft_possible(self, board, current_player, cards, items):
        return super().is_craft_possible(board, current_player, cards, items)

    def is_recruit_possible(self, board):
        possible_clearings = []
        for clearing in board.graph.nodes:
            if any(building['type'].startswith("base") for building in board.graph.nodes[clearing]['buildings']):
                if self.units > 0:
                    possible_clearings.append(clearing)
                    
        return bool(possible_clearings), possible_clearings
               
    def is_revolt_possible(self, board):
        possible_clearings = []
        
        for clearing in board.graph.nodes:
            if any(token['type'] == "sympathy" for token in board.graph.nodes[clearing]['tokens']):
                clearing_type = board.graph.nodes[clearing]['type']
                if self.buildings[f"base_{clearing_type}"] == 1:
                    if self.supporters[clearing_type] + self.supporters["bird"] > 2:
                        possible_clearings.append(clearing)
                
        return bool(possible_clearings), possible_clearings
        
    def is_spread_sympathy_possible(self, board):
        possible_clearings = []
        costs = []
        for clearing in board.graph.nodes:
            if self.tokens["sympathy"] == 10:
                if not any(token['type'] == "sympathy" for token in board.graph.nodes[clearing]['tokens']):
                    self._check_clearing_for_sympathy(board, clearing, possible_clearings, costs)
            else:
                if any(token['type'] == "sympathy" for token in board.graph.nodes[clearing]['tokens']):
                    for neighbor in board.get_adjacent_clearings(clearing):
                        if not any(token['type'] == "sympathy" for token in board.graph.nodes[neighbor]['tokens']):
                            self._check_clearing_for_sympathy(board, neighbor, possible_clearings, costs)
        return bool(possible_clearings), possible_clearings, costs

    def is_mobilize_possible(self, current_player):
        if any(base == 0 for base in self.buildings.values()) or sum(self.supporters.values()) < 5:
            if len(current_player.cards) > 0:
                return True
        return False

    def is_train_possible(self, current_player):
        if len(current_player.cards) > 0 and self.units > 0:
            for base_type, base_count in self.buildings.items():
                if base_count == 0:
                    base_color = base_type.split('_')[1]
                    if any(card['color'] == base_color or card['color'] == "bird" for card in current_player.cards):
                        return True
        return False
        
    def is_move_possible(self, board):
        return super().is_move_possible(board)
    
    def is_battle_possible(self, board):
        return super().is_battle_possible(board)
    
    def is_organize_possible(self, board):
        possible_clearings = []
        for clearing in board.get_clearings_with_units(self.id):
                if not any(token['type'] == "sympathy" or token['type'] == "dungeon" for token in board.graph.nodes[clearing]['tokens']):
                    possible_clearings.append(clearing)
        return bool(possible_clearings), possible_clearings
    
    def get_possible_actions(self, board, actions, current_player, cards, items):
        possible_actions = []
        
        for action in actions:
            is_action_possible_method = getattr(self, f'is_{action}_possible')
            
            if action == "craft":
                if is_action_possible_method(board, current_player, cards, items)[0]:
                    possible_actions.append(action)
                    
            elif action == "mobilize" or action == "train":
                if is_action_possible_method(current_player):
                    possible_actions.append(action)
                    
            elif is_action_possible_method(board)[0]:
                possible_actions.append(action)
            
        return possible_actions
    
############################################################################################################
################################################# ACTIONS ##################################################
############################################################################################################

    def craft(self, display, board, current_player, cards, items):
        super().craft(display, board, current_player, cards, items)

    def mobilize(self, display, current_player):
        card = display.ask_for_cards(current_player, pass_available=True)
        if card == "pass": return
        self.supporters[card['color']] += 1
        current_player.cards.remove(card)
    
    def train(self, display, current_player):
        colors = [base.split('_')[1] for base, count in self.buildings.items() if count == 0]
        cards  = [card['id'] for card in current_player.cards if card['color'] in colors or card['color'] == "bird"]
        card   = display.ask_for_cards(current_player, "id", cards, pass_available=True)
        if card == "pass":return
        self.officers += 1
        self.units -= 1
        current_player.cards.remove(card)
    
    def move(self, display, board, pass_available=True):
        super().move(display, board, pass_available)

    def battle(self, display, lobby, board, cards):
        super().battle(display, lobby, board, cards, pass_available=True)

    def recruit(self, display, board):
        _, clearings = self.is_recruit_possible(board)
        clearing = display.ask_for_clearing(clearings, pass_available=True)
        if clearing == "pass": return
        if self.id not in board.graph.nodes[clearing]['units']:
            board.graph.nodes[clearing]['units'][self.id] = 0
        board.graph.nodes[clearing]['units'][self.id] += 1
        self.units -= 1

    def organize(self, display, board, cards):
        _, clearings = self.is_organize_possible(board)
        clearing = display.ask_for_clearing(clearings, pass_available=True)
        if clearing == "pass": return
        self.units += 1
        board.graph.nodes[clearing]['units'][self.id] -= 1
        board.graph.nodes[clearing]['tokens'].append({"type" : "sympathy", "owner" : self.id})
        #if board.graph.nodes[clearing]['units'][self.id] == 0:
        #    del board.graph.nodes[clearing]['units'][self.id]
    
############################################################################################################
############################################# ACTIONS ANNEXES ##############################################
############################################################################################################ 

    def _check_clearing_for_sympathy(self, board, clearing, possible_clearings, costs):
        clearing_type = board.graph.nodes[clearing]['type']
        cost = 3 if self.tokens["sympathy"] <= 4 else 2 if self.tokens["sympathy"] <= 7 else 1
        if any(board.graph.nodes[clearing]['units'][faction] > 3 for faction in board.graph.nodes[clearing]['units']):
            cost += 1
        if self.supporters[clearing_type] + self.supporters["bird"] >= cost:
            possible_clearings.append(clearing)
            costs.append({
                "clearing": clearing,
                "clearing_type_cost": min(cost, self.supporters[clearing_type]),
                "bird_cost": max(0, cost - self.supporters[clearing_type])
            })

    def spread_sympathy(self, display, board):
        possible, clearings, costs = self.is_spread_sympathy_possible(board)
        while possible:
            clearing = display.ask_for_clearing(clearings, pass_available=True, costs=costs)
            if clearing == "pass": break
        
            cost = 3 if self.tokens["sympathy"] <= 4 else 2 if self.tokens["sympathy"] <= 7 else 1
            if any(board.graph.nodes[clearing]['units'][faction] > 3 for faction in board.graph.nodes[clearing]['units']):
                cost += 1
            
            while self.supporters[board.graph.nodes[clearing]['type']] > 0:
                self.supporters[board.graph.nodes[clearing]['type']] -= 1
            self.tokens["sympathy"] -= 1
            board.graph.nodes[clearing]['tokens'].append({"type" : "sympathy", "faction" : "Alliance"})
            possible, clearings, costs = self.is_spread_sympathy_possible(board)

    def revolt(self, display, board, current_player):
        possible, clearings = self.is_revolt_possible(board)
        while possible:
            clearing = display.ask_for_clearing(clearings, pass_available=True)
            for _ in range(2):
                if self.supporters[board.graph.nodes[clearing]['type']] > 0:
                    self.supporters[board.graph.nodes[clearing]['type']] -= 1
                else:
                    self.supporters["bird"] -= 1

            # Remove sympathy tokens and buildings
            removed_tokens = [token for token in board.graph.nodes[clearing]['tokens'] if token['type'] == "sympathy"]
            removed_buildings = [building for building in board.graph.nodes[clearing]['buildings'] if building['faction'] == "Alliance"]
            
            board.graph.nodes[clearing]['tokens'] = [token for token in board.graph.nodes[clearing]['tokens'] if token['type'] != "sympathy"]
            board.graph.nodes[clearing]['buildings'] = [building for building in board.graph.nodes[clearing]['buildings'] if building['faction'] != "Alliance"]
            
            victory_points = len(removed_tokens) + len(removed_buildings)
            current_player.victory_points += victory_points
            
            # Place warriors in the clearing
            tokens_clearings = board.get_clearings_with_tokens("sympathy")
            for tc in tokens_clearings:
                if board.graph.nodes[tc]["type"] == board.graph.nodes[clearing]["type"] and self.units > 0:
                    board.graph.nodes[clearing]['units'] += 1
                    self.units -= 1
            
            self.officers += 1
            possible, clearings = self.is_revolt_possible(board)

############################################################################################################
############################################### TOUR DE JEU ################################################
############################################################################################################

    def birdsong_phase(self, display, board, current_player):
        
        # 1 Révolte
        self.revolt(display, board, current_player)
        
        # 2 Spread Sympathy
        self.spread_sympathy(display, board)
     
    def daylight_phase(self, display, board, current_player, cards, items):
        possible_actions = self.get_possible_actions(board, self.daylight_actions, current_player, cards, items)
        while possible_actions:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if display.is_button_pass_clicked(event.pos): return 
                    
                    action = display.is_action_button_clicked(pygame.mouse.get_pos())
                    if action in possible_actions:
                        action_methods = {
                            "craft": lambda: self.craft(display, board, current_player, cards, items),
                            "mobilize": lambda: self.mobilize(display, current_player),
                            "train": lambda: self.train(display, current_player)
                        }
                        action_methods[action]()
                        possible_actions = self.get_possible_actions(board, self.daylight_actions, current_player, cards, items)
                display.draw()
                display.draw_actions(self.id, self.daylight_actions, possible_actions)
                pygame.display.flip()        

    def evening_phase(self, display, board, lobby, current_player, cards, items):
        # 1 Military Operations
        possible_actions = self.get_possible_actions(board, self.evening_actions, current_player, cards, items)
        actions_taken = 0
        while possible_actions and actions_taken < self.officers:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if display.is_button_pass_clicked(event.pos): break 
                    
                    action = display.is_action_button_clicked(pygame.mouse.get_pos())
                    if action in possible_actions:
                        action_methods = {
                            "move": lambda: self.move(display, board),
                            "battle": lambda: self.battle(display, lobby, board, cards),
                            "recruit": lambda: self.recruit(display, board),
                            "organize": lambda: self.organize(display, board, cards),
                        }
                        action_methods[action]()
                        actions_taken += 1
                        possible_actions = self.get_possible_actions(board, self.evening_actions, current_player, cards, items)
                display.draw()
                display.draw_actions(self.id, self.evening_actions, possible_actions)
                pygame.display.flip()
        
        # 2 Draw cards
        self.number_card_draw_bonus = sum(1 for base in self.buildings.values() if base == 0)
        self.draw(display, current_player, cards)
    
    def play(self, display, board, lobby, current_player, cards, items):
        self.birdsong_phase(display, board, current_player)
        self.daylight_phase(display, board, current_player, cards, items)
        self.evening_phase(display, board, lobby, current_player, cards, items)