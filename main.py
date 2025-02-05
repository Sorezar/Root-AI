# Internal imports
from board import RootBoard
from display import RootDisplay
from test import RootTest
from config import *
from player import Player
from lobby import Lobby
from items import Items
from cards import Cards
from factions.Marquise import Marquise
from factions.Canopee import Canopee
from factions.Alliance import Alliance
from factions.Vagabond import Vagabond

# External imports
import pygame
import json

def initial_setup(lobby, board, display, cards):

    for player in lobby.players:
        if player.faction.id == 0:
            marquise = player
        elif player.faction.id == 1:
            canopee = player
        elif player.faction.id == 2:
            alliance = player

    # Piocher des cartes pour chaque joueur
    for player in lobby.players:
        player.draw_cards(cards, 3)
         
    # Récupérer la clairière
    dungeon_clearing = display.ask_for_clearing([1, 3, 9, 12])

    # Marquise
    marquise.faction.tokens["dungeon"] = 0
    board.graph.nodes[dungeon_clearing]["tokens"].append({"type": "dungeon", "owner": marquise.faction.id})
    
    adjacent_clearings = board.get_adjacent_clearings(dungeon_clearing)
    start_clearings = adjacent_clearings + [dungeon_clearing]
    
    def _place_building(building, start_clearings=start_clearings):
        start_clearings = board.get_clearing_with_empty_slots(start_clearings) 
        clearing = display.ask_for_clearing(start_clearings)
        marquise.faction.buildings[building] -= 1
        board.graph.nodes[clearing]["buildings"].append({"type": building, "owner": marquise.faction.id})
    
    _place_building("sawmill")
    _place_building("workshop")
    _place_building("recruiter")
    
    roost_clearing = {1: 12, 3: 9, 9: 3, 12: 1}[dungeon_clearing]
    for clearing in board.graph.nodes:
        if clearing != roost_clearing:
            board.graph.nodes[clearing]["units"][marquise.faction.id] = 1
            marquise.faction.units -= 1
        board.update_control(clearing)

    # Canopée
    canopee.faction.buildings["roost"] -= 1
    board.graph.nodes[roost_clearing]["buildings"].append({"type": "roost", "owner": canopee.faction.id})
    canopee.faction.units -= 6
    board.graph.nodes[roost_clearing]["units"][canopee.faction.id] = 6
    board.update_control(roost_clearing)
    
    # Alliance (Debug)
    alliance.faction.units -= 1
    board.graph.nodes[roost_clearing]["units"][alliance.faction.id] = 1
    alliance.faction.buildings["base_fox"] -= 1
    board.graph.nodes[7]["buildings"].append({"type": "base_fox", "owner": alliance.faction.id})
    alliance.faction.tokens["sympathy"] -= 1
    board.graph.nodes[7]["tokens"].append({"type": "sympathy", "owner": alliance.faction.id})

def run(display, lobby, board, cards, items):
    running = True
    
    while running:
        current_player = lobby.get_player(lobby.current_player)
        current_player.faction.play(display, board, lobby, current_player, cards, items)
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                        
        lobby.current_player = (lobby.current_player + 1) % len(lobby.players)
                        
        display.draw()
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":

    # Initialisation des joueurs
    print("Initialisation des joueurs")
    lobby = Lobby()
    lobby.add_player("J1", Marquise())
    lobby.add_player("J2", Canopee()) 
    lobby.add_player("J3", Alliance())
    #lobby.add_player("J4", Vagabond())
    
    board   = RootBoard(MAP_FILE)
    items   = Items()
    tests   = RootTest()
    cards   = Cards(json.load(open(CARDS_FILE)))
    display = RootDisplay(board, lobby, items)
    cards.shuffle()
    
    # Mise en place initiale
    initial_setup(lobby, board, display, cards)
    
    # Tests
    tests.test_adjacency(board)
    tests.test_control(board)
    tests.test_units(board, lobby)
    tests.test_tokens(board)
    tests.test_buildings(board)

    # The boucle
    run(display, lobby, board, cards, items)