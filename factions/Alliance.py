from factions.BaseFaction import Base

# Under development

class Alliance(Base):
    def __init__ (self):
        super().__init__("Alliance de la forêt", 2)
        self.buildings = {}
        self.tokens = {
            "sympathy" : 0
        }
        self.units = 10