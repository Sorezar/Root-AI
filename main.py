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

def initial_setup(lobby, board, display):

    for player in lobby.players:
        if player.faction.id == 0:
            marquise = player
        elif player.faction.id == 1:
            canopee = player

    # Piocher des cartes pour chaque joueur
    for player in lobby.players:
        player.draw_cards(deck, 3)

    # Récupérer la clairière
    selected_clearing = display.ask_for_clearing([1, 3, 9, 12])

    # Marquise
    marquise.faction.tokens["dungeon"] = 0
    board.graph.nodes[selected_clearing]["tokens"].append({"type": "dungeon", "owner": marquise.faction.id})
    opposite_clearing = {1: 12, 3: 9, 9: 3, 12: 1}[selected_clearing]
    for clearing in board.graph.nodes:
        if clearing != opposite_clearing:
            board.graph.nodes[clearing]["units"][marquise.faction.id] = 1
            marquise.faction.units -= 1
        board.update_control(clearing)

    # Canopée
    #canopee.faction.buildings["roost"] = 1
    #board.graph.nodes[opposite_clearing]["buildings"]["roost"] = canopee.faction.name
    canopee.faction.units -= 6
    board.graph.nodes[opposite_clearing]["units"][canopee.faction.id] = 6
    board.update_control(opposite_clearing)

def run(display, lobby):
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if display.is_button_clicked(event.pos):
                    lobby.current_player = (lobby.current_player + 1) % len(lobby.players)
                action = display.is_action_button_clicked(event.pos)
                if action:
                    print(f"Action {action} clicked")
                    # Gérer ici
        display.draw()
        pygame.display.flip()
        display.clock.tick(60)
    pygame.quit()

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
    
    # Deck
    with open(CARDS_FILE, "r") as f:
        deck = json.load(f)
    
    # Initialisation de l'affichage
    print("Initialisation de l'affichage")
    display = RootDisplay(board, lobby, items)
    
    # Mise en place initiale
    initial_setup(lobby, board, display)
    
    # Tests
    print("Tests")
    tests.test_adjacency(board)
    tests.test_control(board)
    tests.test_units(board, lobby)

    # The boucle
    run(display, lobby)