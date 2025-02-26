from factions.BaseFaction import Base
import pygame

class Vagabond(Base):
    def __init__ (self, lobby):
        super().__init__("Vagabond", 3)
        self.units = 0
        self.items = {
            "bag":      [0,0],
            "boot":     [0,0],
            "crossbow": [0,0],
            "hammer":   [0,0],
            "sword":    [0,0],
            "teapot":   [0,0],
            "gold":     [0,0],
            "torch":    [0,0]
        }
        self.damaged_items = {
            "bag":      [0,0],
            "boot":     [0,0],
            "crossbow": [0,0],
            "hammer":   [0,0],
            "sword":    [0,0],
            "teapot":   [0,0],
            "gold":     [0,0],
            "torch":    [0,0]
        }
        self.relationships = {p.faction.id: 0 for p in lobby.players if p.faction.id != 3}
        self.vagabond = "Ranger"
        self.pos = None
        self.quests = [0,0,0]
        self.actions = ["move", "battle", "explore", "aid", "quest", "strike", "repair", "craft"]
        
        gear = {
            "Thief":      {"boot":1,"torch":1,"teapot":1,"sword":1},
            "Tinker":     {"boot":1,"torch":1,"bag":1,"hammer":1},
            "Ranger":     {"boot":1,"torch":1,"crossbow":1,"sword":1},
            "Vagrant":    {"gold":1,"torch":1,"boot":1},
            "Arbiter":    {"boot":1,"torch":1,"sword":2},
            "Scoundrel":  {"boot":2,"torch":1,"crossbow":1},
            "Adventurer": {"boot":1,"torch":1,"hammer":1},
            "Ronin":      {"boot":2,"torch":1,"sword":1},
            "Harrier":    {"gold":1,"torch":1,"sword":1,"crossbow":1}
        }
        for item, qty in gear.get(self.vagabond, {}).items():
            self.items[item][0] = qty

############################################################################################################
###################################### VERIFICATIONS ACTIONS POSSIBLES #####################################
############################################################################################################

    def is_move_possible(self, board):
        possible_clearings = []
        for clearing in board.get_adjacent_clearings(self.pos):
            controlling_faction = board.graph.nodes[clearing]["control"]
            if self.relationships.get(controlling_faction, 0) == -1:
                if self.items["boot"][0] >= 2:
                    possible_clearings.append(clearing)
            else:
                if self.items["boot"][0] >= 1:
                    possible_clearings.append(clearing)
                    
        return bool(possible_clearings), possible_clearings
            
    def is_battle_possible(self, board):
        if self.pos is None or str(self.pos).startswith("F"):
            return False, []
        
        enemy_units = any(units for faction, units in board.graph.nodes[self.pos]["units"].items() if faction != self.id)
        if enemy_units and self.items["sword"][0] >= 1:
            return True, [self.pos]
        
        return False, []
    
    def is_explore_possible(self, board):
        if self.pos is None or str(self.pos).startswith("F"):
            return False, []
        
        if "ruins" in board.graph.nodes[self.pos]["buildings"] and self.items["torch"][0] >= 1:
            return True, [self.pos]
        
        return False, []
    
    def is_aid_possible(self, board):
        if self.pos is None or str(self.pos).startswith("F"):
            return False, []
        
        clearing_color = board.graph.nodes[self.pos]["type"]
        has_appropriate_card = any(card.color == clearing_color or card.color == "bird" for card in self.cards)
        
        if has_appropriate_card:
            for faction, units in board.graph.nodes[self.pos]["units"].items():
                if faction != self.id and units > 0:
                    return True, [self.pos]
        
        return False, []
        
    def is_quest_possible(self, board, cards):
        if self.pos is None or str(self.pos).startswith("F"):
            return False, []
        
        clearing_color = board.graph.nodes[self.pos]["type"]
        possible_quests = []
        
        for quest in cards.active_quests:
            if quest.color == clearing_color:
                if all(self.items[item][0] >= quest.cost.count(item) for item in set(quest.cost)):
                    possible_quests.append(quest)
        
        return bool(possible_quests), possible_quests
        
    def is_strike_possible(self, board):
        if self.pos is None or str(self.pos).startswith("F"):
            return False, []
        
        node = board.graph.nodes[self.pos]
        if any(node["units"].values()) or any(building != "ruins" for building in node["buildings"]) or node["tokens"]:
            return True, [self.pos]
        
        return False, []
         
    def is_repair_possible(self):
        if self.items["hammer"][0] >= 1 and any(qty[0] > 0 or qty[1] > 0 for qty in self.damaged_items.values()):
            return True
        return False
        
    def is_craft_possible(self, board, cards, current_player):
        
        if self.pos is None or str(self.pos).startswith("F"):
            return False, []
        
        objects    = cards.get_objects(current_player)
        craftables = cards.get_cratable_cards(current_player)
        usables = objects + craftables
        
        # Check if the player can craft the item (Plus d'item = pas usable)

        nb_hammers = self.items["hammer"][0]
        clearing_color = board.graph.nodes[self.pos]["type"]

        valid_usables = []
        for card in usables:
            if card['cost_type'] == "none":
                if card['cost'] <= nb_hammers:
                    valid_usables.append(card)
            elif card['cost_type'] == "each": continue # Impossible pour le vagabond
            elif card['cost'] <= nb_hammers and card['cost_type'] == clearing_color:
                valid_usables.append(card)
                
        return bool(valid_usables), valid_usables
        
    def get_possible_actions(self,board, actions, current_player, cards, items):
        possible_actions = []
        
        for action in self.actions:
            is_action_possible_method = getattr(self, f'is_{action}_possible')
            if action == "repair":
                if is_action_possible_method():
                    possible_actions.append(action)
            if action == "move" or action == "battle" or action == "explore" or action == "aid" or action == "strike":
                if is_action_possible_method(board)[0]:
                    possible_actions.append(action)
            if action == "quest":
                if is_action_possible_method(board, cards)[0]:
                    possible_actions.append(action)
            if action == "craft":
                if is_action_possible_method(board, cards, current_player)[0]:
                    possible_actions.append(action)
                    
        return possible_actions
    
############################################################################################################
################################################# ACTIONS ##################################################
############################################################################################################

    

############################################################################################################
############################################# ACTIONS ANNEXES ##############################################
############################################################################################################ 
    
    def refresh_item(self, item):
        self.items[item][0] += 1
        self.items[item][1] -= 1
    
    def get_items_clean_count(self):
        return sum(qty[0] for item, qty in self.items.items() if item not in ["teapot", "gold", "bag"])
    
    def get_items_used_count(self):
        return sum(qty[1] for qty in self.items.values())
    
    def get_damaged_items_clean_count(self):
        return sum(qty[0] for qty in self.items.values()) 
    
    def get_damaged_items_used_count(self):
        return sum(qty[1] for qty in self.items.values())
    
    def get_number_of_items(self):
        total = 0
        total += self.get_items_clean_count()
        total += self.get_items_used_count()
        total += self.get_damaged_items_clean_count()
        total += self.get_damaged_items_used_count()
        return total
    
############################################################################################################
############################################### TOUR DE JEU ################################################
############################################################################################################
    def birdsong_phase(self, display, board, current_player):
        print("Birdsong phase")
        
        # 1 Refresh items
        
        nb_teapots = self.items["teapot"][0]
        nb_refresh  = 2 * nb_teapots + 6
        if nb_refresh >= self.get_items_used_count():
            for item, qty in self.items.items():
                qty[0] += qty[1]
                qty[1] = 0
        else :
            for _ in range(nb_refresh):
                item = display.ask_item_to_refresh()
                self.refresh_item(self, item)
        
        # 2 Slip
        clearings = board.get_adjacent_clearings(self.pos)
        forests = board.get_adjacent_forests(self.pos)
        
        movement = display.ask_for_slip(clearings,forests)
        
        print("Slip to", movement)
        if str(self.pos).startswith("F"):
            board.forests[self.pos]["vagabond"] = False
        else:
            print(board.graph.nodes[self.pos]["units"])
            board.graph.nodes[self.pos]["units"][self.id] -= 1

        if str(movement).startswith("F"):
            board.forests[movement]["vagabond"] = True
        else:
            board.graph.nodes[movement]["units"][self.id] = 1
        
        self.pos = movement
            
        pygame.display.flip()
        
    def daylight_phase(self, display, board, current_player, cards, items):
        print("Daylight phase")
    
        possible_actions = self.get_possible_actions(board, self.actions, current_player, cards, items)
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
                            "move": lambda: self.move(display, board, current_player, cards, items),
                            "battle": lambda: self.battle(display, current_player),
                            "explore": lambda: self.explore(display, current_player),
                            "aid": lambda: self.aid(display, current_player),
                            "quest": lambda: self.quest(display, current_player),
                            "strike": lambda: self.strike(display, current_player),
                            "repair": lambda: self.repair(display, current_player),
                            "craft": lambda: self.craft(display, current_player)
                        }
                        action_methods[action]()
                        possible_actions = self.get_possible_actions(board, self.actions, current_player, cards, items)
                display.draw()
                display.draw_actions(self.id, self.actions, possible_actions)
                pygame.display.flip()   

    
    def evening_phase(self, display, board, lobby, current_player, cards, items):
        print("Evening phase")
        
        # 1 If in forest, repair all items
        if self.pos in board.forests:
            for item, qty in self.damaged_items.items():
                self.items[item][0] += qty[0]
                self.items[item][1] += qty[1]
                self.damaged_items[item] = [0, 0]   
                
        # 2 Draw cards
        self.number_card_draw_bonus = self.items["gold"][0]
        self.draw(display, current_player, cards)
        
        # 3 Remove items overload
        nb_bag = self.items["bag"][0]
        stock  = nb_bag * 2 + 6
        while self.get_number_of_items() >= stock:
            item = display.ask_item_to_remove(self.items, self.damaged_items)
            self.damaged_items[item][item[2]] -= item[1]
            self.items[item][item[2]] -= not item[1]
            
    
    def play(self, display, board, lobby, current_player, cards, items):
        self.birdsong_phase(display, board, current_player)
        self.daylight_phase(display, board, current_player, cards, items)
        self.evening_phase(display, board, lobby, current_player, cards, items)