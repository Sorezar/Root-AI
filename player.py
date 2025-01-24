import random

class Player:
    def __init__(self, name, faction, id):
        self.name    = name
        self.faction = faction
        self.cards   = []
        self.items   = {}
        self.points  = 0
        self.id      = id
        
    def draw_cards(self, cards, number):
        self.cards += cards.draw(number)

    def remove_card(self, card):
        self.cards = [c for c in self.cards if c['id'] != card['id']]

    def add_points(self, points):
        self.points += points
    