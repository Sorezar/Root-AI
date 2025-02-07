from factions.BaseFaction import Base
import pygame

class Marquise(Base):
    def __init__(self):
        super().__init__("Marquise de Chat", 0)
        self.wood_cost = [0, 1, 2, 3, 3, 4]
        self.scoring = {
            "sawmill":   [0, 1, 2, 3, 4, 5],
            "workshop":  [0, 2, 2, 3, 4, 5],
            "recruiter": [0, 1, 2, 3, 3, 5]
        }
        self.buildings = {
            "sawmill":   6,
            "workshop":  6,
            "recruiter": 6
        }
        self.tokens = {
            "wood": 8,
            "dungeon": 1
        }
        self.units = 25
        self.actions = ["build", "recruit", "march", "battle", "overwork", "spend_bird"]
        self.actions_remaining = 3

############################################################################################################
###################################### VERIFICATIONS ACTIONS POSSIBLES #####################################
############################################################################################################ 

    def is_recruit_possible(self, board):
        recruitable_clearings = []
        if self.units > 0:
            for clearing in board.get_clearings_with_recruiters(self.id):
                recruitable_clearings.append(clearing)
                
        if recruitable_clearings:
            return True, recruitable_clearings
        return False, recruitable_clearings

    def is_build_possible(self, board):
        groups = self.get_controlled_groups(board)
        wood_per_group = self.get_wood_per_group(board, groups)
        least_constructed_building = max(self.buildings.values())
        min_wood_cost = self.wood_cost[::-1][least_constructed_building-1]
        
        buildable_clearings = []
        for group, wood_count in zip(groups, wood_per_group):
            if wood_count >= min_wood_cost:
                for clearing in group:
                    if len(board.graph.nodes[clearing]["buildings"]) < board.graph.nodes[clearing]["slots"]:
                        buildable_clearings.append(clearing)
        
        if buildable_clearings:
            return True, buildable_clearings
        return False, buildable_clearings
    
    def is_battle_possible(self, board):
        return super().is_battle_possible(board)
    
    def is_march_possible(self, board):
        move_clearings = []
        controlled_clearings = board.get_controlled_clearings(self.id)
        clearings_with_units = board.get_clearings_with_units(self.id)
        
        for clearing in clearings_with_units:
            if clearing in controlled_clearings:
                for neighbor in board.get_adjacent_clearings(clearing):
                    move_clearings.append((clearing, neighbor))
            else:
                for neighbor in board.get_adjacent_clearings(clearing):
                    if neighbor in controlled_clearings:
                        move_clearings.append((clearing, neighbor))
        
        if move_clearings:
            return True, move_clearings
        return False, move_clearings
    
    def is_spend_bird_possible(self, cards):
        
        for card in cards:
            if card['color'] == "bird":
                return True
        return False
    
    def is_overwork_possible(self, board, cards):
        if self.tokens["wood"] < 1:
                return False
            
        has_bird_card = any(card['color'] == "bird" for card in cards)
        for clearing in board.get_clearings_with_units(self.id):
            if board.graph.nodes[clearing]["type"] in [card['color'] for card in cards if card['color'] != "bird"]:
                if any(building["type"] == "sawmill" and building["owner"] == self.id for building in board.graph.nodes[clearing]["buildings"]):
                    return True
        return has_bird_card and self.buildings["sawmill"] < 6
    
    def get_possible_actions(self, board, cards):
        possible_actions = []
        
        for action in self.actions:
            is_action_possible_method = getattr(self, f'is_{action}_possible')
            if action == "recruit" or action == "build" or action == "march" or action == "battle":
                if is_action_possible_method(board)[0]:
                    possible_actions.append(action)
                    
            elif action == "spend_bird":
                if is_action_possible_method(cards):
                    possible_actions.append(action)
            
            elif action == "overwork":
                if is_action_possible_method(board, cards):
                    possible_actions.append(action)
            
        return possible_actions
   
############################################################################################################
################################################# ACTIONS ##################################################
############################################################################################################

    def recruit(self, display, board):
        is_possible, recruitable_clearings = self.is_recruit_possible(board)
        if is_possible:
            if len(recruitable_clearings) > self.units:
                while self.units > 0:
                    recruit_clearing = display.ask_for_clearing(recruitable_clearings)
                    self.units -= 1
                    if self.id not in board.graph.nodes[recruit_clearing]['units']:
                        board.graph.nodes[recruit_clearing]['units'][self.id] = 0
                    board.graph.nodes[recruit_clearing]["units"][self.id] += 1
            else:
                for r in recruitable_clearings:
                    if self.id not in board.graph.nodes[r]['units']:
                        board.graph.nodes[r]['units'][self.id] = 0
                    self.units -= 1
                    board.graph.nodes[r]["units"][self.id] += 1
        self.actions_remaining -= 1

    def spend_bird(self, display, current_player):
        selected_card = display.ask_for_cards(current_player, criteria="color", values=["bird"], pass_available=True)
        if selected_card == "pass": return
        current_player.remove_card(selected_card)
        self.actions_remaining += 1
        
    def overwork(self, display, board, current_player):
        clearings_with_sawmills = [clearing for clearing in board.graph.nodes if any(building["type"] == "sawmill" and building["owner"] == self.id for building in board.graph.nodes[clearing]["buildings"])]
        type_of_clearing = list(set(board.graph.nodes[clearing]["type"] for clearing in clearings_with_sawmills))
        
        selected_card = display.ask_for_cards(current_player, criteria="color", values=type_of_clearing + ["bird"], pass_available=True)
        if selected_card == "pass": return
        valid_clearings = clearings_with_sawmills if selected_card["color"] == "bird" else [clearing for clearing in clearings_with_sawmills if board.graph.nodes[clearing]["type"] == selected_card["color"]]
        
        selected_clearing = display.ask_for_clearing(valid_clearings, pass_available=True)
        if selected_card == "pass": return
        
        current_player.remove_card(selected_card)
        board.graph.nodes[selected_clearing]["tokens"].append({"type": "wood", "owner": self.id})
        
        self.actions_remaining -= 1
    
    def build(self, display, board, current_player):
        _, clearings = self.is_build_possible(board)
        clearing = display.ask_for_clearing(clearings, pass_available=True)
        if clearing == "pass": return 
        wood_costs = []
        [wood_costs.append(self.wood_cost[::-1][building-1]) for building in self.buildings.values()]
              
        print("wood costs", wood_costs)
              
        groups = self.get_controlled_groups(board)
        wood_per_group = self.get_wood_per_group(board, groups)
        for group, wood_count in zip(groups, wood_per_group):
            if clearing in group:
                max_wood = wood_count
                                
        building, cost = display.ask_for_building_cats(board.graph.nodes[clearing]["pos"], wood_costs, max_wood, self.buildings)
                  
        self.use_wood_for_building(board, group, clearing, cost)   
        current_player.points += self.scoring[building][6 - self.buildings[building]]           
        self.buildings[building] -= 1
        board.graph.nodes[clearing]["buildings"].append({"type": building, "owner": self.id})
            
        board.update_control(clearing)
        self.actions_remaining -= 1
  
    def march(self, display, board):  
        for _ in range(2):
            result = super().move(display, board, pass_available=True)
            if result == "pass":
                if _ == 1:
                    self.actions_remaining -= 1
                return
        self.actions_remaining -= 1
    
    def battle(self, display, lobby, board, cards):
        result = super().battle(display, lobby, board, cards, pass_available=True)
        if result == "pass": return
        self.actions_remaining -= 1
    
############################################################################################################
############################################# ACTIONS ANNEXES ##############################################
############################################################################################################        

    def choose_wood_distribution(self, display, board):
        clearings_with_sawmills = []
        for clearing in board.graph.nodes:
            for building in board.graph.nodes[clearing]["buildings"]:
                if building["type"] == "sawmill" and building["owner"] == self.id:
                    clearings_with_sawmills.append(clearing)
                    
        while self.tokens['wood'] > 0:
            selected_clearing = display.ask_for_clearing(clearings_with_sawmills)
            board.graph.nodes[selected_clearing]["tokens"].append({"type": "wood", "owner": self.id})
            self.tokens['wood'] -= 1
            clearings_with_sawmills.remove(selected_clearing)

    def produce_wood(self, board):
        for clearing in board.graph.nodes:
            for building in board.graph.nodes[clearing]["buildings"]:
                if building["type"] == "sawmill":
                    board.graph.nodes[clearing]["tokens"].append({"type": "wood", "owner": self.id})
                    self.tokens["wood"] -= 1

    def use_wood_for_building(self, board, group, clearing, cost):
        wood_needed = cost
        visited = set()
        queue = [(clearing, 0)]

        while queue and wood_needed > 0:
            current_clearing, distance = queue.pop(0)
            if current_clearing in visited or current_clearing not in group: continue
            visited.add(current_clearing)

            tokens = board.graph.nodes[current_clearing]["tokens"]
            for token in tokens:
                if token["type"] == "wood" and wood_needed > 0:
                    tokens.remove(token)
                    wood_needed -= 1

            for neighbor in board.get_adjacent_clearings(current_clearing):
                if neighbor not in visited:
                    queue.append((neighbor, distance + 1))
                    
        self.tokens["wood"] += cost
        
    def get_controlled_groups(self, board):
        controlled_clearings = [clearing for clearing in board.graph.nodes if board.graph.nodes[clearing]["control"] == self.id]
        visited = set()
        groups = []

        def dfs(clearing, group):
            visited.add(clearing)
            group.append(clearing)
            
            for neighbor in board.get_adjacent_clearings(clearing):
                if neighbor in controlled_clearings and neighbor not in visited:
                    dfs(neighbor, group)

        for clearing in controlled_clearings:
            if clearing not in visited:
                group = []
                dfs(clearing, group)
                groups.append(group)

        return groups

    def get_wood_per_group(self, board, groups):
        wood_per_group = []
        for group in groups:
            wood_count = 0
            for clearing in group:
                for token in board.graph.nodes[clearing]["tokens"]:
                    if token["type"] == "wood":
                        wood_count += 1
            wood_per_group.append(wood_count)
        return wood_per_group
    
############################################################################################################
############################################### TOUR DE JEU ################################################
############################################################################################################

    def birdsong_phase(self, display, board, current_player, cards, lobby):
        print("Start Birdsong phase")
        # Gestion des effets de début de tour
        
        cards.resolve_start_birdsong_effect(current_player, lobby, board, display)
        
        if 6 - self.buildings["sawmill"] < self.tokens['wood']:
            self.produce_wood(board)
        else:
            self.choose_wood_distribution(display, board)
        
        print("Birdsong phase")
        cards.resolve_birdsong_effect(current_player, lobby, board, display)
        print("End Birdsong phase")
        
    def daylight_phase(self, display, lobby, board, current_player, cards, items):
        print("Start Daylight phase")
        
        # 1 - Crafts
        super().craft(display, board, current_player, cards, items)
    
        # 2 - Actions
        
        self.actions_remaining = 3
        while self.actions_remaining > 0:
            
            for event in pygame.event.get():
                possible_actions = self.get_possible_actions(board, current_player.cards)
                
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if display.is_button_pass_clicked(event.pos): return 
                    
                    action = display.is_action_button_clicked(pygame.mouse.get_pos())
                    
                    if action in possible_actions:
                        action_methods = {
                            "spend_bird": lambda: self.spend_bird(display, lobby.get_player(lobby.current_player)),
                            "march": lambda: self.march(display, board),
                            "recruit": lambda: self.recruit(display, board),
                            "build": lambda: self.build(display, board, current_player),
                            "overwork": lambda: self.overwork(display, board, lobby.get_player(lobby.current_player)),
                            "battle": lambda: self.battle(display, lobby, board, cards)
                        }
                        action_methods[action]()
                        
                display.draw()
                display.draw_actions(self.id, self.actions, possible_actions)
                pygame.display.flip()
        return

    def evening_phase(self, display, current_player, cards):
        self.draw(display, current_player, cards)
    
    def play(self, display, board, lobby, current_player, cards, items):
        self.birdsong_phase(display, board, current_player, cards, lobby)
        self.daylight_phase(display, lobby, board, current_player, cards, items)
        self.evening_phase(display, current_player, cards)