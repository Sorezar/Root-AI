from factions.Marquise import Marquise
from factions.Canopee   import Canopee
from factions.Alliance import Alliance
from factions.Vagabond import Vagabond
import random
import json

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

    def remove_card(self, card_id):
        self.cards = [card for card in self.cards if card['id'] != card_id]

    def add_points(self, points):
        self.points += points
        
    def play_turn(self):
        self.faction.birdsong_phase()
        self.faction.daylight_phase()
        self.faction.evening_phase()
    
    def get_controlled_clearings(self, board):
        return [clearing for clearing in board.graph.nodes if board.graph.nodes[clearing]["control"] == self.faction.id]
    
    def get_clearings_with_units(self, board):
        return [clearing for clearing in board.graph.nodes if board.graph.nodes[clearing]["units"].get(self.faction.id, 0) > 0]