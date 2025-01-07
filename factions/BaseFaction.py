class Base:
    def __init__(self, name, id):
        self.id    = id
        self.name  = name
        self.units = 0
        self.buildings = {}
        
    def place_unit(self, clearing_id, board):
                
        if self.units <= 0 :
            raise ValueError(f"Plus d'unités à placer.")
        
        if clearing_id not in board.graph.nodes:
            raise ValueError(f"Clairière {clearing_id} inexistante.")

        clearing = board.graph.nodes[clearing_id]
        clearing["units"][self.id] = clearing["units"].get(self.id, 0) + 1
        self.units -= 1
        board.update_control(clearing_id)
    
    def place_building(self, clearing_id, building_type):
        raise NotImplementedError()
    
    def move_unit(self, from_clearing, to_clearing, board):
        if to_clearing not in board.get_adjacent_clearings(from_clearing):
            raise ValueError("Déplacement invalide. Les clairières ne sont pas adjacentes.")

        units = board.graph.nodes[from_clearing]["units"]
        if units.get(self.name, 0) == 0:
            raise ValueError(f"Aucune unité de {self.name} dans la clairière {from_clearing}.")

        # Mise à jour des unités
        board.graph.nodes[from_clearing]["units"][self.id] -= 1
        board.graph.nodes[to_clearing]["units"][self.id] = board.graph.nodes[to_clearing]["units"].get(self.id, 0) + 1

        # Mise à jour du contrôle
        board.update_control(from_clearing)
        board.update_control(to_clearing)