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
    alliance.faction.units -= 1
    board.graph.nodes[roost_clearing]["units"][alliance.faction.id] = 1
    alliance.faction.buildings["base_fox"] -= 1
    board.graph.nodes[7]["buildings"].append({"type": "base_fox", "owner": alliance.faction.id})
    alliance.faction.tokens["sympathy"] -= 1
    board.graph.nodes[7]["tokens"].append({"type": "sympathy", "owner": alliance.faction.id})

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
    
def build(display, board, current_player):
    # Pour la Marquise
    if current_player.faction.id == 0:
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
        selected_clearing = display.ask_for_clearing(clearings_with_sawmills)
        board.graph.nodes[selected_clearing]["tokens"].append({"type": "wood", "owner": current_player.faction.id})
        current_player.faction.tokens['wood'] -= 1
        clearings_with_sawmills.remove(selected_clearing)

def overwork(display, board, current_player):
    clearings_with_sawmills = []
    type_of_clearing = []
                        
    for clearing in board.graph.nodes:
        for building in board.graph.nodes[clearing]["buildings"]:
            if building["type"] == "sawmill" and building["owner"] == current_player.faction.id:
                clearings_with_sawmills.append(clearing)
                if board.graph.nodes[clearing]["type"] not in type_of_clearing:
                    type_of_clearing.append(board.graph.nodes[clearing]["type"])
                        
    selected_card = display.ask_for_cards(current_player, criteria="color", values=type_of_clearing + ["bird"])
                        
    if selected_card["color"] == "bird":
        valid_clearings = clearings_with_sawmills
    else:
        valid_clearings = [clearing for clearing in clearings_with_sawmills if board.graph.nodes[clearing]["type"] == selected_card["color"]]
                        
    selected_clearing = display.ask_for_clearing(valid_clearings)
                        
    current_player.remove_card(selected_card)
    board.graph.nodes[selected_clearing]["tokens"].append({"type": "wood", "owner": current_player.faction.id})
    
def battle(display, lobby, board, current_player):
    
    def _have_ennemy_things(clearing, thing, board, current_player):
        if thing == "units":
            return any(unit > 0 and faction_id != current_player.faction.id for faction_id, unit in board.graph.nodes[clearing][thing].items())
        if thing == "buildings":
            return any(b["owner"] != current_player.faction.id and b["owner"] != None for b in board.graph.nodes[clearing][thing])
        return any(t["owner"] != current_player.faction.id for t in board.graph.nodes[clearing][thing])
    
    attackable_clearings = [clearing for clearing in board.graph.nodes if board.graph.nodes[clearing]["units"].get(current_player.faction.id, 0) > 0 and any(_have_ennemy_things(clearing, thing, board, current_player) for thing in ["units", "buildings", "tokens"])]
    attack_clearing = display.ask_for_clearing(attackable_clearings)
                        
    ennemy_factions = {faction_id for thing in ["units", "buildings", "tokens"]
                        for item in board.graph.nodes[attack_clearing][thing]
                        if (faction_id := (item if thing == "units" else item['owner'])) != current_player.faction.id
                        and (thing != "units" or board.graph.nodes[attack_clearing]["units"].get(faction_id, 0) > 0)}
    ennemy_factions.discard(None)
    ennemy_factions = list(ennemy_factions)
                        
    # Get the ennemy faction
    defender_faction_id = ennemy_factions[0] if len(ennemy_factions) == 1 else display.ask_for_enemy(attack_clearing, ennemy_factions)
                                               
    # Roll the dice
    dices =  [random.randint(0, 3), random.randint(0, 3)]
    attacker_roll, defender_roll = sorted(dices, reverse=defender_faction_id != 2)
                        
    # Calculate damage
    attacker_damage = min(attacker_roll, board.graph.nodes[attack_clearing]["units"].get(current_player.faction.id, 0))
    defender_damage = min(defender_roll, board.graph.nodes[attack_clearing]["units"].get(defender_faction_id, 0))
                        
    # Si défenseur sans défense
    attacker_damage += 1 if board.graph.nodes[attack_clearing]["units"].get(defender_faction_id, 0) == 0 else 0
                        
    # TODO : Gérer les dégâts supplémentaires
                        
    def _inflict_damage(lobby, board, clearing, faction_id, base_damage):
        damage = base_damage
        faction = lobby.get_player(faction_id).faction
                            
        # Inflict damage to units
        units = board.graph.nodes[clearing]["units"].get(faction_id, 0)
        units_lost = min(damage, units)
        if faction_id in board.graph.nodes[clearing]["units"]:
            board.graph.nodes[clearing]["units"][faction_id] -= units_lost
        else:
            board.graph.nodes[clearing]["units"][faction_id] = 0
        faction.units += units_lost
        damage -= units_lost
                            
        # Inflict damage to buildings and tokens
        if damage > 0:
            buildings = [b for b in board.graph.nodes[clearing]["buildings"] if b["owner"] == faction_id]
            tokens = [t for t in board.graph.nodes[clearing]["tokens"] if t["owner"] == faction_id]
            pieces = buildings + tokens
                                
            if damage >= len(pieces):
                for building in buildings:
                    faction.buildings[building["type"]] += 1
                for token in tokens:
                    faction.tokens[token["type"]] += 1
                board.graph.nodes[clearing]["buildings"] = [b for b in board.graph.nodes[clearing]["buildings"] if b["owner"] != faction_id]
                board.graph.nodes[clearing]["tokens"] = [t for t in board.graph.nodes[clearing]["tokens"] if t["owner"] != faction_id]
            else:
                original_player = lobby.current_player
                lobby.current_player = faction_id
                for _ in range(damage):
                    removed, type = display.ask_what_to_remove(clearing, faction_id)
                    if type == 'building':
                        board.graph.nodes[clearing]['buildings'].remove(removed)
                        faction.buildings[removed['type']] += 1
                    elif type == 'token':
                        board.graph.nodes[clearing]['tokens'].remove(removed)
                        faction.tokens[removed['type']] += 1
                lobby.current_player = original_player
                                    
    _inflict_damage(lobby, board, attack_clearing, defender_faction_id, attacker_damage)
    _inflict_damage(lobby, board, attack_clearing, current_player.faction.id, defender_damage)
    
    # Update control
    board.update_control(attack_clearing)

def spend_bird(display, current_player):
    selected_card = display.ask_for_cards(current_player, criteria="color", values=["bird"])
    current_player.remove_card(selected_card)

def recruit(display, board, current_player):
        
    recruiters_clearings = current_player.get_clearings_with_recruiters(board)
    print("Ca commence le recrutement")
    
    # Pour la Marquise     
    if current_player.faction.id == 0:            
        if len(recruiters_clearings) > current_player.faction.units :
            while current_player.faction.is_recruitments_possible():
                recruit_clearing = display.ask_for_clearing(current_player.get_clearings_with_recruiters(board))
                current_player.faction.units -= 1
                board.graph.nodes[recruit_clearing]["units"][current_player.faction.id] += 1
        else:
            for r in recruiters_clearings:
                current_player.faction.units -= 1
                board.graph.nodes[r]["units"][current_player.faction.id] += 1
                
    # Pour Canopée
    elif current_player.faction.id == 1:
        print("Ca recrute")
        if len(recruiters_clearings) > current_player.faction.units :
            print("1er cas")
            while current_player.faction.is_recruitments_possible():
                recruit_clearing = display.ask_for_clearing(current_player.get_clearings_with_recruiters(board))
                current_player.faction.units -= 1
                board.graph.nodes[recruit_clearing]["units"][current_player.faction.id] += 1
        else:
            for r in recruiters_clearings:
                print("2eme cas")
                current_player.faction.units -= 1
                board.graph.nodes[r]["units"][current_player.faction.id] += 1

def resolve_decree(display, lobby, board, current_player):
    canopee = current_player.faction
    actions = ["recruit", "move", "battle", "build"]
    for action in actions:
        print(f"Action: {action}")
        for color in canopee.decrees[action]:
            print(f"Action: {action}, colors: {color}")
            if action == "recruit":
                print("Recruit")
                if not current_player.is_action_available("Recruit", board):
                    print("pas d'action disponible")
                    trigger_crisis(display, lobby, board, current_player)
                    return
                print("On fait l'action")
                recruit(display, board, current_player)
            elif action == "move":
                print("Move")
                if not current_player.is_action_available("Move", board):
                    trigger_crisis(display, lobby, board, current_player)
                    return
                movement_phase(display, board, current_player)
            elif action == "battle":
                if not current_player.is_action_available("Battle", board):
                    trigger_crisis(display, lobby, board, current_player)
                    return
                battle(display, lobby, board, current_player)
            elif action == "build":
                if not current_player.is_action_available("Build", board):
                    trigger_crisis(display, lobby, board, current_player)
                    return
                build(display, board, current_player)

def trigger_crisis(display, lobby, board, current_player):
    canopee = current_player.faction
    bird_cards = sum(color == "bird" for action in canopee.decrees.values() for color in action)
    current_player.points = max(0, current_player.points - bird_cards)
    canopee.decrees = {action: [] for action in canopee.decrees}
    # Choisir un nouveau leader (non implémenté ici)
    lobby.current_player = (lobby.current_player + 1) % len(lobby.players)

def run(display, lobby, board):
    running = True
    cat_actions_remaining = 3
    
    while running:
        current_player = lobby.get_player(lobby.current_player)
        
        if current_player.faction.id == 1:  # Canopée
            for _ in range(2):
                selected_card, action = display.ask_for_decree_card_and_action(current_player)
                current_player.faction.decrees[action].append(selected_card["color"])
                current_player.remove_card(selected_card)
                choice = display.ask_to_continue_or_finish()
                if choice == "finish":
                    break
            print(current_player.faction.decrees)
            resolve_decree(display, lobby, board, current_player)
            
            # Joueur suivant
            lobby.current_player = (lobby.current_player + 1) % len(lobby.players)

        
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
                        spend_bird(display, current_player)
                        cat_actions_remaining += 1
                    
                    if action == "March":
                        for _ in range(2):
                            movement_phase(display, board, current_player)
                            if _ == 0: 
                                if not display.ask_for_second_march():
                                    break
                        cat_actions_remaining -= 1
                    
                    if action == "Move":
                        movement_phase(display, board, current_player)
                        cat_actions_remaining -= current_player.faction.id == 0
                    
                    if action == "Recruit":
                        recruit(display, board, current_player)
                        cat_actions_remaining -= current_player.faction.id == 0
                            
                    if action == "Build":
                        build(display, board, current_player)
                        cat_actions_remaining -= current_player.faction.id == 0
                            
                    if action == "Overwork":
                        overwork(display, board, current_player)
                        cat_actions_remaining -= current_player.faction.id == 0
                        
                    if action == "Battle":
                        battle(display, lobby, board, current_player)
                        cat_actions_remaining -= current_player.faction.id == 0
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
    lobby.add_player("J3", Alliance())
    
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