from factions.BaseFaction import Base

# Under development

class Vagabond(Base):
    def __init__ (self):
        super().__init__("Vagabond", 3)
        self.buildings = {}
        self.units = 0
        