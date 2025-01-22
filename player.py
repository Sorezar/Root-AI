import random

class Player:
    def __init__(self, name, faction, id):
        self.name    = name
        self.faction = faction
        self.cards   = []
        self.items   = {}
        self.points  = 0
        self.id      = id

    def draw_cards(self, deck, count=1):
        for _ in range(count):
            card = random.choice(deck)
            self.cards.append(card)
            deck.remove(card)

    def remove_card(self, card):
        self.cards = [c for c in self.cards if c['id'] != card['id']]

    def add_points(self, points):
        self.points += points
        
    # Pour plus tard lors de la mise au propre
    def play_turn(self):
        self.faction.birdsong_phase()
        self.faction.daylight_phase()
        self.faction.evening_phase()
    
    def get_possible_actions(self, board):
        if self.faction.id == 0:
            return self.faction.get_possible_actions(board, self.cards)
        if self.faction.id == 1:
            return self.faction.get_possible_actions(board)
    