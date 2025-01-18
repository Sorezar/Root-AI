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

    def produce_wood(self, board):
        for clearing in board.graph.nodes:
            for building in board.graph.nodes[clearing]["buildings"]:
                if building["type"] == "sawmill":
                    board.graph.nodes[clearing]["tokens"].append({"type": "wood", "owner": self.id})
                    self.tokens["wood"] -= 1

    # Vérifie si le recrutement d'unités est possible
    def is_recruitments_possible(self):
        if self.buildings["recruiter"] < 6 and self.units > 0:
            return True        
        else :
            return False

    def use_wood_for_building(self, board, group, clearing, cost):
        wood_needed = cost
        wood_used = 0
        visited = set()
        queue = [(clearing, 0)]

        while queue and wood_needed > 0:
            current_clearing, distance = queue.pop(0)
            if current_clearing in visited:
                continue
            visited.add(current_clearing)

            tokens = board.graph.nodes[current_clearing]["tokens"]
            for token in tokens:
                if token["type"] == "wood" and wood_needed > 0:
                    tokens.remove(token)
                    wood_needed -= 1
                    wood_used += 1

            for neighbor in board.graph.neighbors(current_clearing):
                if neighbor not in visited:
                    queue.append((neighbor, distance + 1))
        self.tokens["wood"] += cost
        
    def overwork(self, board, cards):
        has_bird_card = any(card['color'] == "bird" for card in cards)
        for clearing in self.get_clearings_with_units(board):
            if board.graph.nodes[clearing]["type"] in [card['color'] for card in self.cards if card['color'] != "bird"]:
                if any(building["type"] == "sawmill" and building["owner"] == self.faction.id for building in board.graph.nodes[clearing]["buildings"]):
                    return True
        return has_bird_card and self.faction.buildings["sawmill"] < 6

    def is_building_possible(self, board):
        groups = self._get_controlled_groups(board)
        wood_per_group = self._get_wood_per_group(board, groups)
        least_constructed_building = max(self.buildings.values())
        min_wood_cost = self.wood_cost[::-1][least_constructed_building-1]
        
        buildable_clearings = []

        for group, wood_count in zip(groups, wood_per_group):
            if wood_count >= min_wood_cost:
                for clearing in group:
                    if len(board.graph.nodes[clearing]["buildings"]) < board.graph.nodes[clearing]["slots"]:
                        buildable_clearings.append(clearing)
        if buildable_clearings:
            return True, buildable_clearings
        return False, buildable_clearings
    
    def _get_controlled_groups(self, board):
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

    def _get_wood_per_group(self, board, groups):
        wood_per_group = []
        for group in groups:
            wood_count = 0
            for clearing in group:
                for token in board.graph.nodes[clearing]["tokens"]:
                    if token["type"] == "wood":
                        wood_count += 1
            wood_per_group.append(wood_count)
        return wood_per_group