from factions.BaseFaction import Base

class Marquise(Base):
    def __init__(self):
        super().__init__("Marquise de Chat", 0)
        self.wood_cost = [0, 1, 2, 3, 3, 4]
        self.scoring = {
            "sawmill":   [0, 1, 2, 3, 4, 5],
            "workshop":  [0, 2, 2, 3, 4, 5],
            "recruiter": [0, 1, 2, 3, 3, 5]
        }
        self.buildings = {
            "sawmill":   6,
            "workshop":  6,
            "recruiter": 6
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
        
    # Vérifie si le recrutement d'unités est possible
    def is_recruitments_possible(self):
        if self.buildings["recruiter"] < len(self.scoring['recruiter']) and self.units > 0:
            return True        
        else :
            return False
    
    # Vérifie si la construction d'un bâtiment est possible
    def is_building_possible(self, board):
        for clearing_id, clearing in board.graph.nodes.items():
            if len(clearing["buildings"]) < clearing["slots"]:
                least_constructed_building = max(self.buildings.values())
                min_wood_cost = self.wood_cost[::-1][least_constructed_building-1]
                max_wood = self.how_much_wood_to_gather(clearing_id, board)
                if max_wood >= min_wood_cost:
                    return True

        return False

    # Récupère le nombre de bois récoltable dans une clairière
    def how_much_wood_to_gather(self, clearing_id, board):
        max_wood = 0
        counted_clearings = set()
        for clearing_id, clearing in board.graph.nodes.items():
            wood = 0
            if clearing["control"] == self.id and clearing_id not in counted_clearings:
                for token in clearing["tokens"]:
                    if token["type"] == "wood":
                        wood += 1
                counted_clearings.add(clearing_id)
                for target_id, target in board.graph.nodes.items():
                    if target["control"] == self.id and self.is_path_controlled(clearing_id, target_id, board) and target_id not in counted_clearings:
                        for token in target["tokens"]:
                            if token["type"] == "wood":
                                wood += 1
                        counted_clearings.add(target_id)
            if wood > max_wood:
                max_wood = wood
        return max_wood

    # Vérifie la présence d'un chemin contrôlé entre deux clairières
    def is_path_controlled(self, start, end, board):
        visited = set()
        stack = [start]
    
        while stack:
            current = stack.pop()
            if current == end:
                return True
            if current not in visited:
                visited.add(current)
                neighbors = board.graph.neighbors(current)
                for neighbor in neighbors:
                    if board.graph.nodes[neighbor]["control"] == self.id:
                        stack.append(neighbor)
        return False