from board import RootBoard
from display import RootDisplay
from test import RootTest
from config import *
from player import Player
from lobby import Lobby
from factions.Marquise import Marquise
from factions.Canopee import Canopee

if __name__ == "__main__":

    # Initialisation des joueurs
    
    print("Initialisation des joueurs")
    lobby = Lobby()
    
    lobby.add_player("J1", Marquise())
    lobby.add_player("J2", Canopee())    
    
    # Initialisation de la carte
    print("Initialisation de la carte")
    board    = RootBoard(MAP_FILE)
    
    # Initialisation des tests
    print("Initialisation des tests")
    test     = RootTest()
    
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
    
    # Tests
    print("Tests")
    test.test_adjacency(board)
    test.test_control(board)
    test.test_units(board)

    # Initialisation de l'affichage
    print("Initialisation de l'affichage")
    display = RootDisplay(board)
    display.run(lobby.players[0].name, lobby.get_scores())
    
    