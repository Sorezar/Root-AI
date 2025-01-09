from factions.BaseFaction import Base

class Marquise(Base):
    def __init__(self):
        super().__init__("Marquise de Chat", 0)
        self.buildings = {
            "sawmill": 0,
            "workshop": 0,
            "recruiter": 0
        }
        self.tokens = {
            "wood": 8,
            "dungeon": 1
        }
        self.units = 25
        self.actions = ["Build", "Recruit", "March", "Battle", "Overwork", "Spend Bird"]

    def build_structure(self, clearing_id, structure_type, board):
        if structure_type not in self.buildings:
            raise ValueError(f"Bâtiment {structure_type} inconnu.")

        clearing = board.graph.nodes[clearing_id]

        # Vérifie s'il y a de la place pour un bâtiment
        if len(clearing["buildings"]) >= clearing["slots"]:
            raise ValueError(f"Pas assez de slots dans la clairière {clearing_id}.")

        # Vérifie que la Marquise contrôle la clairière
        if clearing["control"] != self.name:
            raise ValueError(f"La Marquise doit contrôler la clairière {clearing_id} pour construire.")

        # Ajoute le bâtiment
        clearing["buildings"][structure_type] = self.name
        self.buildings[structure_type] += 1
        board.add_points(self.name, 1) 

    def produce_wood(self, board):
        pass

    def spend_wood(self, amount):
        pass

    def recruit_units(self, clearing_id, board):
        clearing = board.graph.nodes[clearing_id]

        if clearing["buildings"].get("recruiter") != self.name:
            raise ValueError(f"Aucun recruteur dans la clairière {clearing_id}.")
        
        self.place_unit(clearing_id, board)
