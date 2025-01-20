class Base:
    def __init__(self, name, id):
        self.id    = id
        self.name  = name
        self.units = 0
        self.buildings = {}
        self.number_card_draw_bonus = 0
        
        
    def place_building(self, clearing_id, building_type):
        raise NotImplementedError()
    
    def move_unit(self, from_clearing, to_clearing, board, number_of_units):

        units = board.graph.nodes[from_clearing]["units"]

        # Mise à jour des unités
        board.graph.nodes[from_clearing]["units"][self.id] -= number_of_units
        board.graph.nodes[to_clearing]["units"][self.id] = board.graph.nodes[to_clearing]["units"].get(self.id, 0) + number_of_units

        # Mise à jour du contrôle
        board.update_control(from_clearing)
        board.update_control(to_clearing)
    
    def is_recruitments_possible(self, board):
        raise NotImplementedError()
    