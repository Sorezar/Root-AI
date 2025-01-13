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

    def is_recruitments_possible(self):
        if self.buildings["roost"] < len(self.scoring['roost']) and self.units > 0:
            return True 
        else :
            return False