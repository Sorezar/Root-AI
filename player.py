import random

class Player:
    def __init__(self, name, faction, id):
        self.name    = name
        self.faction = faction
        self.cards   = []
        self.crafted_cards = []
        self.items   = {
            "bag":      0,
            "boot":     0,
            "crossbow": 0,
            "hammer":   0,
            "sword":    0,
            "teapot":   0,
            "gold":     0,
            "torch":    0
        }
        self.points  = 0
        self.id      = id
        
    def draw_cards(self, cards, number):
        self.cards += cards.draw(number)

    def remove_card(self, card):
        self.cards = [c for c in self.cards if c['id'] != card['id']]
    
    def remove_crafted_card(self, card):
        self.crafted_cards = [c for c in self.crafted_cards if c['id'] != card['id']]

    def add_points(self, points):
        self.points += points
        
    def draw_card_by_id(self, card_id, deck):
        card = next((c for c in deck.deck if c['id'] == card_id), None)
        if card:
            self.cards.append(card)
            deck.deck.remove(card)
    