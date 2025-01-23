from factions.BaseFaction import Base

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
        battle_clearings = []
        for clearing in board.get_clearings_with_units(self.id):
            for token in board.graph.nodes[clearing]["tokens"]:
                if token["owner"] != self.id:
                    battle_clearings.append(clearing) if clearing not in battle_clearings else None
            for building in board.graph.nodes[clearing]["buildings"]:
                if building["owner"] != self.id and building["type"] != "ruins":
                    battle_clearings.append(clearing) if clearing not in battle_clearings else None
            if sum(units for owner, units in board.graph.nodes[clearing]["units"].items() if owner != self.id) > 0:
                battle_clearings.append(clearing) if clearing not in battle_clearings else None
        if battle_clearings:
            return True, battle_clearings
        return False, battle_clearings
    
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
        super().recruit(display, board)
        self.actions_remaining -= 1

    def spend_bird(self, display, current_player):
        selected_card = display.ask_for_cards(current_player, criteria="color", values=["bird"])
        current_player.remove_card(selected_card)
        self.actions_remaining += 1
        
    def overwork(self, display, board, current_player):
        clearings_with_sawmills = [clearing for clearing in board.graph.nodes if any(building["type"] == "sawmill" and building["owner"] == self.id for building in board.graph.nodes[clearing]["buildings"])]
        type_of_clearing = list(set(board.graph.nodes[clearing]["type"] for clearing in clearings_with_sawmills))
        
        selected_card = display.ask_for_cards(current_player, criteria="color", values=type_of_clearing + ["bird"])
        valid_clearings = clearings_with_sawmills if selected_card["color"] == "bird" else [clearing for clearing in clearings_with_sawmills if board.graph.nodes[clearing]["type"] == selected_card["color"]]
        
        selected_clearing = display.ask_for_clearing(valid_clearings)
        current_player.remove_card(selected_card)
        board.graph.nodes[selected_clearing]["tokens"].append({"type": "wood", "owner": self.id})
        
        self.actions_remaining -= 1
    
    def build(self, display, board):
        _, clearings = self.is_build_possible(board)
        clearing = display.ask_for_clearing(clearings)
        wood_costs = []
        [wood_costs.append(self.wood_cost[::-1][building-1]) for building in self.buildings.values()]
                                
        groups = self.get_controlled_groups(board)
        wood_per_group = self.get_wood_per_group(board, groups)
        for group, wood_count in zip(groups, wood_per_group):
            if clearing in group:
                max_wood = wood_count
                                
        building, cost = display.ask_for_building_cats(board.graph.nodes[clearing]["pos"], wood_costs, max_wood, self.buildings)
                                
        self.buildings[building] -= 1
        board.graph.nodes[clearing]["buildings"].append({"type": building, "owner": self.id})
        self.use_wood_for_building(board, group, clearing, cost)
        
        board.update_control(clearing)
        self.actions_remaining -= 1
  
    def march(self, display, board):  
        for _ in range(2):
            super().move(display, board)
            if _ == 0 and not display.ask_for_second_march():
                break
        self.actions_remaining -= 1
    
    def battle(self, display, lobby, board):
        super().battle(display, lobby, board)
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
        wood_used = 0
        visited = set()
        queue = [(clearing, 0)]

        while queue and wood_needed > 0:
            current_clearing, distance = queue.pop(0)
            if current_clearing in visited or current_clearing not in group:
                continue
            visited.add(current_clearing)

            tokens = board.graph.nodes[current_clearing]["tokens"]
            for token in tokens:
                if token["type"] == "wood" and wood_needed > 0:
                    tokens.remove(token)
                    wood_needed -= 1
                    wood_used += 1

            for neighbor in board.graph.neighbors(current_clearing):
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
            for neighbor in board.graph.neighbors(clearing):
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

    def birdsong_phase(self, display, board):
            if 6 - self.buildings["sawmill"] < self.tokens['wood']:
                self.produce_wood(board)
            else:
                self.choose_wood_distribution(display, board)

    def daylight_phase(self, display, lobby, board):
        self.actions_remaining = 3
        
        # 1 - Implémentation du crafting
        
        
        # 2 - Implémentation des actions
        

    def evening_phase(self, display, current_player, deck):
        
        # Draw a card
        self.draw(self, display, current_player, deck)
        