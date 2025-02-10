from factions.BaseFaction import Base
import pygame

class Vagabond(Base):
    def __init__ (self, lobby):
        super().__init__("Vagabond", 3)
        self.units = 0
        self.items = {
            "bag":      [0,0,0],
            "boot":     [0,0,0],
            "crossbow": [0,0,0],
            "hammer":   [0,0,0],
            "sword":    [0,0,0],
            "teapot":   [0,0,0],
            "gold":     [0,0,0],
            "torch":    [0,0,0]
        }
        self.relationships = {p.faction.id: 0 for p in lobby.players if p.faction.id != 3}
        self.vagabond = "ranger"
        
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
            self.items[item] = [qty, 0, 0]
            
        self.pos = 1
        self.actions = ["move", "battle", "explore", "aid", "quest", "strike", "repair_or_craft"]


############################################################################################################
############################################# ACTIONS ANNEXES ##############################################
############################################################################################################ 
    
    def refresh_item(self, item):
        self.items[item][0] += 1
        self.items[item][1] -= 1
    
    def get_items_clean_count(self, items):
        return sum(qty[0] for qty in items.values())
    
    def get_items_used_count(self, items):
        return sum(qty[1] for qty in items.values())
    
############################################################################################################
############################################### TOUR DE JEU ################################################
############################################################################################################
    def birdsong_phase(self, display, board, current_player):
        print("Birdsong phase")
        
        # 1 Refresh items
        
        nb_teapots = self.items["teapot"][0]
        nb_refresh  = 2 * nb_teapots + 6
        if nb_refresh >= self.get_items_used_count(self.items):
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
        if movement.startswith("F"):
            self.pos = movement
            board.forests[self.pos]["vagabond"] = True
            
        pygame.display.flip()
        
    def daylight_phase(self, display, board, current_player, cards, items):
        print("Daylight phase")
    
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
        print("Evening phase")
        
        # TODO CHECK SI LA REPARATION REFRESH OU PAS
        
        # 1 If in forest, repair all items
        if self.pos in board.forests:
            for item, qty in self.items.items():
                qty[0] += qty[2]
                qty[2] = 0
                
        # 2 Draw cards
        self.number_card_draw_bonus = self.items["gold"][0]
        self.draw(display, current_player, cards)
        
        # 4 Remove items overload
        nb_bag = self.items["bag"][0]
        stock  = nb_bag * 2 + 6
        while self.get_items_clean_count(self.items) >= stock:
            item = display.ask_item_to_remove()
            self.items[item][0] -= 1
    
    def play(self, display, board, lobby, current_player, cards, items):
        self.birdsong_phase(display, board, current_player)
        self.daylight_phase(display, board, current_player, cards, items)
        self.evening_phase(display, board, lobby, current_player, cards, items)