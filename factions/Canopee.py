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
                print("Recruitment possible")
                return True
            
        return False