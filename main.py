from board import RootBoard
from display import RootDisplay
from test import RootTest
from config import *
from player import Player
from lobby import Lobby
from items import Items
from factions.Marquise import Marquise
from factions.Canopee import Canopee
from factions.Alliance import Alliance
from factions.Vagabond import Vagabond

import json

if __name__ == "__main__":

    # Initialisation des joueurs
    print("Initialisation des joueurs")
    lobby = Lobby()
    lobby.add_player("J1", Marquise())
    lobby.add_player("J2", Canopee())    
    
    # Initialisation de la carte
    print("Initialisation de la carte")
    board = RootBoard(MAP_FILE)
    
    # Initialisation des objets
    print("Initialisation des objets")
    items = Items()
    
    # Initialisation des tests
    print("Initialisation des tests")
    tests = RootTest()
    
    try:
        lobby.get_player("J1").faction.place_unit(2, board)
        lobby.get_player("J1").faction.place_unit(1, board)
        lobby.get_player("J1").faction.place_unit(1, board)
        lobby.get_player("J1").faction.place_unit(3, board)
        lobby.get_player("J2").faction.place_unit(1, board)
        lobby.get_player("J2").faction.place_unit(2, board)
        lobby.get_player("J2").faction.place_unit(2, board)
    except ValueError as e:
        print(e)
    
    # Deck
    with open(CARDS_FILE, "r") as f:
        deck = json.load(f)

    # Piocher des cartes pour chaque joueur
    for player in lobby.players:
        player.draw_cards(deck, 5)
        
    # Tests
    print("Tests")
    tests.test_adjacency(board)
    tests.test_control(board)
    tests.test_units(board)

    # Initialisation de l'affichage
    print("Initialisation de l'affichage")
    display = RootDisplay(board, lobby, items)
    display.run()