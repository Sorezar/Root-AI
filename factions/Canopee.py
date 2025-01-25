from factions.BaseFaction import Base

class Canopee(Base):
    def __init__(self):
        super().__init__("Dynastie de la Canopée", 1)
        self.scoring = {
            "roost":   [0, 1, 2, 3, 4, 4, 5]
        }
        self.buildings = {
            "roost": 7
        }
        self.units = 20
        self.decrees = {
            "recruit": [],
            "move": [],
            "battle": [],
            "build": []
        }

############################################################################################################
###################################### VERIFICATIONS ACTIONS POSSIBLES #####################################
############################################################################################################ 

    def is_recruit_possible(self, board):
        recruitable_clearings = []
        
        if len(self.decrees["recruit"]) == 0:
            return False, recruitable_clearings
        
        for clearing in board.graph.nodes:
            if ("bird" in self.decrees["recruit"] or board.graph.nodes[clearing]['type'] in self.decrees["recruit"]) and any(building['type'] == "roost" for building in board.graph.nodes[clearing]["buildings"]):
                recruitable_clearings.append(clearing)
        
        if recruitable_clearings:
            return True, recruitable_clearings
        return False, recruitable_clearings
    
    def is_build_possible(self, board):
        
        buildable_clearings = []
        
        if self.buildings["roost"] > 0:
            for clearing in board.graph.nodes:
                if board.graph.nodes[clearing]["control"] == self.id:
                    if ("bird" in self.decrees["build"] or board.graph.nodes[clearing]['type'] in self.decrees["build"]):
                        if not any(building['type'] == "roost" for building in board.graph.nodes[clearing]["buildings"]):
                            buildable_clearings.append(clearing)
                            
        if buildable_clearings:
            return True, buildable_clearings
        return False, buildable_clearings
    
    def is_battle_possible(self, board):
        battle_clearings = []
        for clearing in board.get_clearings_with_units(self.id):
            clearing_type = board.graph.nodes[clearing]['type']
            if "bird" in self.decrees["battle"] or clearing_type in self.decrees["battle"]:
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
    
    def is_move_possible(self, board):
        move_clearings = []
        controlled_clearings = board.get_controlled_clearings(self.id)
        clearings_with_units = board.get_clearings_with_units(self.id)
        
        for clearing in clearings_with_units:
            clearing_type = board.graph.nodes[clearing]['type']
            if "bird" in self.decrees["move"] or clearing_type in self.decrees["move"]:
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
    
    def get_possible_actions(self, board):
        possible_actions = []
        for action in self.decrees.keys():
            is_action_available_method = getattr(self, f'is_{action}_possible')
            if is_action_available_method(board)[0]:
                possible_actions.append(action)
        return possible_actions
    
############################################################################################################
################################################# ACTIONS ##################################################
############################################################################################################

    def recruit(self, display, board):
        super().recruit(display, board)
        
    def move(self, display, board):
        # Rajouter gestion de l'achat du bateau
        
        # Récup from_clearing et to_clearing
        _, move_options = self.is_move_possible(board)
        from_clearing = display.ask_for_clearing([option[0] for option in move_options])
        to_clearing = display.ask_for_clearing([option[1] for option in move_options if option[0] == from_clearing])
        
        # Nb unités
        max_units = board.graph.nodes[from_clearing]["units"][self.id]
        if max_units > 1:
            units_to_move = display.ask_for_units_to_move(max_units, board.graph.nodes[to_clearing]["pos"])
        else:
            units_to_move = 1
            
        # Mise à jour des unités
        board.graph.nodes[from_clearing]["units"][self.id] -= units_to_move
        board.graph.nodes[to_clearing]["units"][self.id] = board.graph.nodes[to_clearing]["units"].get(self.id, 0) + units_to_move

        # Mise à jour du contrôle
        board.update_control(from_clearing)
        board.update_control(to_clearing)
        
    def battle(self, display, lobby, board):
        super().battle(display, lobby, board)
        
    def build(self, display, board):
        _, clearings = self.is_build_possible(board)
        clearing = display.ask_for_clearing(clearings)
        self.buildings['roost'] -= 1
        board.graph.nodes[clearing]["buildings"].append({"type": "roost", "owner": self.id})
    
        board.update_control(clearing)

############################################################################################################
############################################## GESTION DECRET ##############################################
############################################################################################################

    def resolve_decree(self, display, lobby, board):
        for action in self.decrees.keys():
            for color in self.decrees[action]:
                if action == "recruit":
                    possible, _ = self.is_recruit_possible(board)
                    if not possible:
                        self.trigger_crisis(display, lobby)
                        return
                    self.recruit(display, board)
                    
                elif action == "move":
                    possible, _ = self.is_move_possible(board)
                    if not possible:
                        self.trigger_crisis(display, lobby)
                        return
                    self.move(display, board)
                    
                elif action == "battle":
                    possible, _ = self.is_battle_possible(board)
                    if not possible:
                        self.trigger_crisis(display, lobby)
                        return
                    self.battle(display, lobby, board)
                    
                elif action == "build":
                    possible, _ = self.is_build_possible(board)
                    if not possible:
                        self.trigger_crisis(display, lobby)
                        return
                    self.build(display, board)
                    
    def trigger_crisis(self, display, lobby):
        bird_cards = sum(color == "bird" for action in self.decrees.values() for color in action)
        self.points = max(0, lobby.players[lobby.current_player].points - bird_cards)
        self.decrees = {action: [] for action in self.decrees}
        
        # Afficher le message de crise
        display.draw_message("La Canopée tombe en crise !", duration=2000)
        
        # Choisir un nouveau leader (non implémenté ici)

############################################################################################################
############################################### TOUR DE JEU ################################################
############################################################################################################

    def birdsong_phase(self, current_player, display, cards):
        
        # 1 - Si main vide on pioche une carte - v
        if current_player.cards == []:
            current_player.cards.draw_cards(cards)
            
        # 2 - Add 1 or 2 cards to the decree - v
        for _ in range(2):
            selected_card = display.ask_for_cards(current_player, pass_available=(_ != 0))
            if selected_card == "pass": break
            
            action = display.ask_for_action(selected_card)
            self.decrees[action].append(selected_card["color"])
            current_player.remove_card(selected_card)
        
        # 3 - If no roosts, place a roost and 3 warriors in the clearing with the fewest total pieces - x

    def daylight_phase(self, display, lobby, board):
            
        # 1 - Implémentation du crafting - x
        
        
        # 2 - Résolution du décret - v
        self.resolve_decree(display, lobby, board)

    def evening_phase(self, display, current_player, cards):
        
        # Score points - v
        current_player.add_points(self.scoring["roost"][7 - self.buildings["roost"] - 1])
        
        # Draw a card - v
        self.draw(display, current_player, cards)
        
    def play(self, display, board, lobby, current_player, cards, items):
        self.birdsong_phase(current_player, display, cards)
        self.daylight_phase(display, lobby, board)
        self.evening_phase(display, current_player, cards)
        