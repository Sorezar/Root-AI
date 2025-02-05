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

    def is_craft_possible(self, display, board, current_player, cards, items):
        super().is_craft_possible(display, board, current_player, cards, items)

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
        
        for clearing in board.graph.nodes:
            if any(token['type'] == "sympathy" for token in board.graph.nodes[clearing]['tokens']):
                for neighbor in board.graph.neighbors(clearing):
                    if not any(token['type'] == "sympathy" for token in board.graph.nodes[neighbor]['tokens']):
                        clearing_type = board.graph.nodes[neighbor]['type']
                        cost = 3 if self.tokens["sympathy"] <= 4 else 2 if self.tokens["sympathy"] <= 7 else 1
                        if any(board.graph.nodes[neighbor]['units'][faction] > 3 for faction in board.graph.nodes[neighbor]['units']):
                            cost += 1
                        if self.supporters[clearing_type] + self.supporters["bird"] >= cost:
                            possible_clearings.append(neighbor)
                   
        return bool(possible_clearings), possible_clearings

    def get_possible_actions(self, board, actions):
        possible_actions = []
        
        for action in actions:
            is_action_possible_method = getattr(self, f'is_{action}_possible')
            if is_action_possible_method(board)[0]:
                possible_actions.append(action)
            
        return possible_actions
    
############################################################################################################
############################################### TOUR DE JEU ################################################
############################################################################################################

    def birdsong_phase(self, display, board, current_player):
        
        # 1 Révolte
        possible, clearings = self.is_revolt_possible(board)
        print("revolt possible", possible)
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
        
        # 2 Spread Sympathy
        possible, clearings = self.is_spread_sympathy_possible(board)
        print("spread possible", possible)
        while possible:
            clearing = display.ask_for_clearing(clearings, pass_available=True)
            if clearing == "pass": break
        
            cost = 3 if self.tokens["sympathy"] <= 4 else 2 if self.tokens["sympathy"] <= 7 else 1
            if any(board.graph.nodes[clearing]['units'][faction] > 3 for faction in board.graph.nodes[clearing]['units']):
                cost += 1
            
            while self.supporters[board.graph.nodes[clearing]['type']] > 0:
                self.supporters[board.graph.nodes[clearing]['type']] -= 1
            self.tokens["sympathy"] -= 1
            board.graph.nodes[clearing]['tokens'].append({"type" : "sympathy", "faction" : "Alliance"})
            possible, clearings = self.is_spread_sympathy_possible(board)
        
     
    def daylight_phase(self, display, board, current_player, cards, items):
        possible_actions = self.get_possible_actions(board, self.daylight_actions)
        print("actions", possible_actions)
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
                            "craft": lambda: super().craft(display, board, current_player, cards, items),
                            "mobilize": lambda: self.mobilize(display, board),
                            "train": lambda: self.train(display, board, cards)
                        }
                        action_methods[action]()
                        
                display.draw()
                display.draw_actions(self.id, self.daylight_actions, possible_actions)
                pygame.display.flip()
        return        

    def evening_phase(self, display, board, current_player, cards):
        # 1 Military Operations
        possible_actions = self.get_possible_actions(board, self.evening_actions)
        print("actions", possible_actions)
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
                            "move": lambda: self.move(display, board),
                            "battle": lambda: self.battle(display, board),
                            "recruit": lambda: self.recruit(display, board, cards),
                            "organize": lambda: self.organize(display, board, cards),
                        }
                        action_methods[action]()
                        
                display.draw()
                display.draw_actions(self.id, self.evening_actions, possible_actions)
                pygame.display.flip()
        return
    
    def play(self, display, board, lobby, current_player, cards, items):
        self.birdsong_phase(display, board, current_player)
        self.daylight_phase(display, board, current_player, cards, items)
        self.evening_phase(display, board, current_player, cards)