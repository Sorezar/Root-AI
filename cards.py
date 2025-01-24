import random

class Cards:
    def __init__(self, deck):
        self.deck = deck
        self.discard = []
        
    def draw(self, number=1):
        cards = []
        for _ in range(number):
            if not self.deck:
                self.deck = self.discard
                self.discard = []
                self.shuffle()
            cards.append(self.deck.pop())
        return cards
        
    def shuffle(self):
        random.shuffle(self.deck)