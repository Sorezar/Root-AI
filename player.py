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

    def remove_card(self, card):
        self.cards = [c for c in self.cards if c['id'] != card['id']]

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
    
    def get_clearings_with_recruiters(self, board):
        if self.faction.id == 0:
            return [clearing for clearing in board.graph.nodes if any(building["type"] == "recruiter" for building in board.graph.nodes[clearing]["buildings"])]
        if self.faction.id == 1:
            return [clearing for clearing in board.graph.nodes if any(building["type"] == "roost" for building in board.graph.nodes[clearing]["buildings"])]
        if self.faction.id == 2:
            return [clearing for clearing in board.graph.nodes if any(token["type"] == "sympathy" for token in board.graph.nodes[clearing]["tokens"])]
        if self.faction.id == 3:
            return None
    
    def get_available_actions(self, board):
        available_actions = []
        for action in self.faction.actions:
            if self.is_action_available(action, board):
                available_actions.append(action)
        return available_actions
    
    def is_action_available(self, action, board):
        
        if action == 'Overwork':
            if self.faction.tokens["wood"] < 1:
                return False
            
            has_bird_card = any(card['color'] == "bird" for card in self.cards)
            for clearing in self.get_clearings_with_units(board):
                if board.graph.nodes[clearing]["type"] in [card['color'] for card in self.cards if card['color'] != "bird"]:
                    if any(building["type"] == "sawmill" and building["owner"] == self.faction.id for building in board.graph.nodes[clearing]["buildings"]):
                        return True
            return has_bird_card and self.faction.buildings["sawmill"] < 6
        
        if action == 'Battle':
            for clearing in self.get_clearings_with_units(board):
                for token in board.graph.nodes[clearing]["tokens"]:
                    if token["owner"] != self.faction.id:
                        return True
                for building in board.graph.nodes[clearing]["buildings"]:
                    if building["owner"] != self.faction.id and building["type"] != "ruins":
                        return True
                for unit_owner in board.graph.nodes[clearing]["units"]:
                    if unit_owner != self.faction.id:
                        return True
            return False
        
        if action == 'Build':
            possible , _ = self.faction.is_building_possible(board)
            return possible
        
        if action == 'Recruit':
            return self.faction.is_recruitments_possible()
        
        if action == 'Spend Bird':
            for card in self.cards:
                if card['color'] == "bird":
                    return True
            return False
        
        if action == "March" or action == "Move":
            return bool(self.get_clearings_with_units(board))
        # Ajoutez d'autres vérifications pour d'autres actions