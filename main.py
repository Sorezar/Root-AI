# Internal imports
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

# External imports
import json

def initial_setup(lobby, board, display):

    for player in lobby.players:
        if player.faction.id == 0:
            marquise = player
        elif player.faction.id == 1:
            canopee = player
        elif player.faction.id == 2:
            alliance = player

    # Piocher des cartes pour chaque joueur
    for player in lobby.players:
        player.draw_cards(deck, 3)

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
    #alliance.faction.units -= 1
    #board.graph.nodes[roost_clearing]["units"][alliance.faction.id] = 1
    #alliance.faction.buildings["base_fox"] -= 1
    #board.graph.nodes[7]["buildings"].append({"type": "base_fox", "owner": alliance.faction.id})
    #alliance.faction.tokens["sympathy"] -= 1
    #board.graph.nodes[7]["tokens"].append({"type": "sympathy", "owner": alliance.faction.id})

def run(display, lobby, board):
    running = True
    
    while running:
        current_player = lobby.get_player(lobby.current_player)
        
        # Canopée
        if current_player.faction.id == 1:  
            for _ in range(2):
                selected_card, action = display.ask_for_decree_card_and_action(current_player)
                current_player.faction.decrees[action].append(selected_card["color"])
                current_player.remove_card(selected_card)
                if _ == 0 and display.ask_to_continue_or_finish() == "finish":
                    break
            current_player.faction.resolve_decree(display, lobby, board)
            
            # Joueur suivant
            lobby.current_player = (lobby.current_player + 1) % len(lobby.players)
        
        for event in pygame.event.get():
            
            # Si le  chat n'a plus d'actions
            if current_player.faction.id == 0 :
                if current_player.faction.actions_remaining == 0:
                    current_player.faction.actions_remaining = 3
                    lobby.current_player = (lobby.current_player + 1) % len(lobby.players)
            
            # Si on quitte le jeu
            if event.type == pygame.QUIT:
                running = False 
            
            # Si on clique sur un bouton
            elif event.type == pygame.MOUSEBUTTONDOWN:
                
                # Bouton Pass
                if display.is_button_pass_clicked(event.pos):
                    lobby.current_player = (lobby.current_player + 1) % len(lobby.players)
                    if lobby.current_player == 0:
                        current_player = lobby.get_player(lobby.current_player)
                        current_player.faction.actions_remaining = 3
                        
                        if 6 - current_player.faction.buildings["sawmill"] < current_player.faction.tokens['wood']:
                            current_player.faction.produce_wood(board)
                        else :
                            current_player.faction.choose_wood_distribution(display, board)
                            
                    
                # Si on clique sur une action de faction
                action = display.is_action_button_clicked(event.pos)
                if action in current_player.get_possible_actions(board):
                    
                    if action == "spend_bird":
                        current_player.faction.spend_bird(display, current_player)
                    
                    if action == "march":
                        current_player.faction.march(display, board)
                    
                    if action == "move":
                        current_player.faction.move(display, board)
                    
                    if action == "recruit":
                        current_player.faction.recruit(display, board)
                            
                    if action == "build":
                        current_player.faction.build(display, board)
                            
                    if action == "overwork":
                        current_player.faction.overwork(display, board, current_player)
                        
                    if action == "battle":
                        current_player.faction.battle(display, lobby, board)
                        
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
    #lobby.add_player("J3", Alliance())
    
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
    tests.test_tokens(board)
    tests.test_buildings(board)

    # The boucle
    run(display, lobby, board)