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
import random

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
    
    
def movement_phase(display, board, current_player):
    # Rajouter gestion de l'achat du bateau
    
    # Récup from_clearing
    clearing_with_units = current_player.get_clearings_with_units(board)
    controled_clearings = current_player.get_controlled_clearings(board) 
    from_clearing = display.ask_for_clearing(clearing_with_units)
    
    # Récup to_clearing
    adjacent_clearings = board.get_adjacent_clearings(from_clearing)
    adjacent_and_controlled_clearings = [clearing for clearing in adjacent_clearings if clearing in controled_clearings]
    if from_clearing not in controled_clearings:
        to_clearing = display.ask_for_clearing(adjacent_and_controlled_clearings)
    else :
        to_clearing = display.ask_for_clearing(adjacent_clearings)
    
    # Nb unités
    max_units = board.graph.nodes[from_clearing]["units"][current_player.faction.id]
    if max_units > 1:
        units_to_move = display.ask_for_units_to_move(max_units, board.graph.nodes[to_clearing]["pos"])
    else:
        units_to_move = 1
    current_player.faction.move_unit(from_clearing, to_clearing, board, units_to_move)
    
def build_phase_cat(display, board, current_player):
    _, clearings = current_player.faction.is_building_possible(board)
    clearing = display.ask_for_clearing(clearings)
    wood_costs = []
    [wood_costs.append(current_player.faction.wood_cost[::-1][building-1]) for building in current_player.faction.buildings.values()]
                            
    groups = current_player.faction._get_controlled_groups(board)
    wood_per_group = current_player.faction._get_wood_per_group(board, groups)
    for group, wood_count in zip(groups, wood_per_group):
        if clearing in group:
            max_wood = wood_count
                            
    building, cost = display.ask_for_building_cats(board.graph.nodes[clearing]["pos"], wood_costs, max_wood, current_player)
                            
    current_player.faction.buildings[building] -= 1
    board.graph.nodes[clearing]["buildings"].append({"type": building, "owner": current_player.faction.id})
    current_player.faction.use_wood_for_building(board, group, clearing, cost)
    board.update_control(clearing)

def choose_wood_distribution(display, board, current_player):
    clearings_with_sawmills = []
    for clearing in board.graph.nodes:
        for building in board.graph.nodes[clearing]["buildings"]:
            if building["type"] == "sawmill" and building["owner"] == current_player.faction.id:
                clearings_with_sawmills.append(clearing)
    while current_player.faction.tokens['wood'] > 0:
        print(current_player.faction.tokens['wood'])
        selected_clearing = display.ask_for_clearing(clearings_with_sawmills)
        board.graph.nodes[selected_clearing]["tokens"].append({"type": "wood", "owner": current_player.faction.id})
        current_player.faction.tokens['wood'] -= 1
        clearings_with_sawmills.remove(selected_clearing)

    
def run(display, lobby, board):
    running = True
    cat_actions_remaining = 3
    
    while running:
        current_player = lobby.get_player(lobby.current_player)
        
        for event in pygame.event.get():
            
            # Si le joueur actuel est le chat, et qu'il a plus d'actions
            if cat_actions_remaining == 0:
                lobby.current_player = (lobby.current_player + 1) % len(lobby.players)
                if current_player.faction.id == 0:
                    cat_actions_remaining = 3
            
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
                        cat_actions_remaining = 3
                        if 6 - current_player.faction.buildings["sawmill"] < current_player.faction.tokens['wood']:
                            current_player.faction.produce_wood(board)
                        else :
                            choose_wood_distribution(display, board, current_player)
                    
                # Si on clique sur une action de faction
                action = display.is_action_button_clicked(event.pos)
                if action in current_player.get_available_actions(board):
                    
                    if action == "Spend Bird":
                        selected_card = display.ask_for_cards(current_player, criteria="color", values=["bird"])
                        current_player.remove_card(selected_card)
                        cat_actions_remaining += 1
                    
                    if action == "March" or action == "Move":
                        movement_phase(display, board, current_player)
                        if current_player.faction.id == 0:
                            cat_actions_remaining -= 1 
                    
                    if action == "Recruit":
                        
                        # Pour la Marquise
                        if current_player.faction.id == 0:
                            recruiters_clearings = []
                            for clearing in board.graph.nodes:
                                for b in board.graph.nodes[clearing]['buildings']:
                                    if b["type"] == "recruiter":
                                        recruiters_clearings.append(clearing)
                            
                            if len(recruiters_clearings) > current_player.faction.units :
                                while current_player.faction.is_recruitments_possible():
                                    recruit_clearing = display.ask_for_clearing(current_player.get_clearings_with_recruiters(board))
                                    current_player.faction.units -= 1
                                    board.graph.nodes[recruit_clearing]["units"][current_player.faction.id] += 1
                            else:
                                for r in recruiters_clearings:
                                    current_player.faction.units -= 1
                                    board.graph.nodes[r]["units"][current_player.faction.id] += 1
                            cat_actions_remaining -= 1
                            
                    if action == "Build":
                        # Pour la Marquise
                        if current_player.faction.id == 0:
                            build_phase_cat(display, board, current_player)
                            cat_actions_remaining -= 1
                            
                    if action == "Overwork":
                        clearings_with_sawmills = []
                        type_of_clearing = []
                        
                        for clearing in board.graph.nodes:
                            for building in board.graph.nodes[clearing]["buildings"]:
                                if building["type"] == "sawmill" and building["owner"] == current_player.faction.id:
                                    clearings_with_sawmills.append(clearing)
                                    if board.graph.nodes[clearing]["type"] not in type_of_clearing:
                                        type_of_clearing.append(board.graph.nodes[clearing]["type"])
                        
                        selected_card = display.ask_for_cards(current_player, criteria="color", values=type_of_clearing)
                        selected_clearing = display.ask_for_clearing(clearings_with_sawmills)
                        
                        current_player.remove_card(selected_card)
                        board.graph.nodes[selected_clearing]["tokens"].append({"type": "wood", "owner": current_player.faction.id})
                        
                        cat_actions_remaining -= 1
                        
                    if action == "Battle":
                        
                        # Get the clearing to attack
                        attackable_clearings = current_player.get_attackable_clearings(board)
                        attack_clearing = display.ask_for_clearing(attackable_clearings)
                        
                        # Get the enemy faction to attack
                        enemy_factions = board.get_enemy_factions_in_clearing(attack_clearing, current_player.faction.id)
                        enemy_faction = display.ask_for_enemy(attack_clearing, enemy_factions)
                        
                        # Roll the dice
                        dices =  [random.randint(0, 3), random.randint(0, 3)]
                        
                        if enemy_faction != 2 :
                            attacker_roll = max(dices)
                            defender_roll = min(dices)
                        else :
                            attacker_roll = min(dices)
                            defender_roll = max(dices)
                        
                        # Calculate damage
                        attacker_damage = min(attacker_roll, board.graph.nodes[attack_clearing]["units"][current_player.faction.id])
                        defender_damage = min(defender_roll, board.graph.nodes[attack_clearing]["units"][enemy_faction])
                        
                        # Apply damage
                        for i in range(attacker_damage):
                            
                            # Remove units
                            
                            # Remove tokens and/or buildings
                            
                            board.graph.nodes[attack_clearing]["units"][current_player.faction.id] -= 1
                        
                        # Update control
                        board.update_control(attack_clearing)
                        
                    
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
    tests.test_tokens(board)
    tests.test_buildings(board)

    # The boucle
    run(display, lobby, board)