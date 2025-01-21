class Base:
    def __init__(self, name, id):
        self.id    = id
        self.name  = name
        self.units = 0
        self.buildings = {}
        self.number_card_draw_bonus = 0
        
        
    def place_building(self, clearing_id, building_type):
        raise NotImplementedError()
    
    def move_unit(self, from_clearing, to_clearing, board, number_of_units):

        units = board.graph.nodes[from_clearing]["units"]

        # Mise à jour des unités
        board.graph.nodes[from_clearing]["units"][self.id] -= number_of_units
        board.graph.nodes[to_clearing]["units"][self.id] = board.graph.nodes[to_clearing]["units"].get(self.id, 0) + number_of_units

        # Mise à jour du contrôle
        board.update_control(from_clearing)
        board.update_control(to_clearing)
    
    def is_recruitments_possible(self, board):
        recruitable_clearings = []
        if self.units > 0:
            for clearing in board.get_clearings_with_recruiters(self.id):
                recruitable_clearings.append(clearing)
                
        if recruitable_clearings:
            return True, recruitable_clearings
        return False, recruitable_clearings
    
    def is_building_possible(self, board):
        raise NotImplementedError()
    
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
    
    def is_move_possible(self, board):
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