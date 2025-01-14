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
        
    def is_building_possible(self, board):
        groups = self.get_controlled_groups(board)
        wood_per_group = self.get_wood_per_group(board, groups)
        least_constructed_building = max(self.buildings.values())
        min_wood_cost = self.wood_cost[::-1][least_constructed_building-1]

        for group, wood_count in zip(groups, wood_per_group):
            if wood_count >= min_wood_cost:
                for clearing in group:
                    if len(board.graph.nodes[clearing]["buildings"]) < board.graph.nodes[clearing]["slots"]:
                        return True
        return False
    
    def get_controlled_groups(self, board):
        controlled_clearings = [clearing for clearing in board.graph.nodes if board.graph.nodes[clearing]["control"] == self.id]
        visited = set()
        groups = []

        def dfs(clearing, group):
            visited.add(clearing)
            group.append(clearing)
            for neighbor in board.graph.neighbors(clearing):
                if neighbor in controlled_clearings and neighbor not in visited:
                    dfs(neighbor, group)

        for clearing in controlled_clearings:
            if clearing not in visited:
                group = []
                dfs(clearing, group)
                groups.append(group)

        return groups

    def get_wood_per_group(self, board, groups):
        wood_per_group = []
        for group in groups:
            wood_count = 0
            for clearing in group:
                for token in board.graph.nodes[clearing]["tokens"]:
                    if token["type"] == "wood":
                        wood_count += 1
            wood_per_group.append(wood_count)
        return wood_per_group