from factions.BaseFaction import Base

class Canopee(Base):
    def __init__(self):
        super().__init__("Dynastie de la Canopée", 1)
        self.buildings = {
            "roost": 0
        }
        self.units = 20
        self.actions = []
