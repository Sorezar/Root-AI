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
        self.actions = []
        self.decrees = {
            "recruit": [],
            "move": [],
            "battle": [],
            "build": []
        }

    def is_recruitments_possible(self, board):
        if len(self.decrees["recruit"]) == 0:
            return False
        
        for decree_type in self.decrees:
            for action in self.decrees[decree_type]:
                print(f"{decree_type}: {action}")
        
        for clearing in board.graph.nodes:
            if ("bird" in self.decrees["recruit"] or board.graph.nodes[clearing]['type'] in self.decrees["recruit"]) and any(building['type'] == "roost" for building in board.graph.nodes[clearing]["buildings"]):
                return True
            
        return False
    
    def is_building_possible(self, board):
        
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