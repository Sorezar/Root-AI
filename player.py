from factions.Marquise import Marquise
from factions.Canopee   import Canopee
from factions.Alliance import Alliance
from factions.Vagabond import Vagabond
import random
import json

class Player:
    def __init__(self, name, faction):
        self.name    = name
        self.faction = faction
        self.cards   = []
        self.items   = {}
        self.points  = 0


    def draw_cards(self, deck, count=1):
        for _ in range(count):
            card = random.choice(deck)
            self.cards.append(card)
            deck.remove(card)

    def remove_card(self, card_id):
        self.cards = [card for card in self.cards if card['id'] != card_id]

    def add_points(self, points):
        self.points += points