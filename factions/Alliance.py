from factions.BaseFaction import Base

# Under development

class Alliance(Base):
    def __init__ (self):
        super().__init__("Alliance de la forêt", 2)
        self.buildings = {
            "base_fox" : 1,
            "base_rabbit" : 1,
            "base_mouse" : 1
        }
        self.tokens = {
            "sympathy" : 10
        }
        self.units = 10
        self.actions = ["Recruit", "Move", "Battle", "Spread Sympathy", "Spend Sympathy"]
        
    def is_recruitments_possible(self, board):
        if self.tokens["sympathy"] < 10 and self.units > 0:
            return True 
        else :
            return False
        
    def is_building_possible(self, board):
        return super().is_building_possible(board)