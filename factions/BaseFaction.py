import random
import pygame
class Base:
    def __init__(self, name, id):
        self.id    = id
        self.name  = name
        self.units = 0
        self.buildings = {}
        self.tokens = {}
        self.actions = []
        self.number_card_draw_bonus = 0
        self.phase = "birdsong"
        self.builders = {
            "fox": 0,
            "mouse": 0,
            "rabbit": 0,
        }

############################################################################################################
###################################### VERIFICATIONS ACTIONS POSSIBLES #####################################
############################################################################################################            

    def is_recruit_possible(self, board):
        recruitable_clearings = []
        if self.units > 0:
            for clearing in board.get_clearings_with_recruiters(self.id):
                recruitable_clearings.append(clearing)
                
        if recruitable_clearings:
            return True, recruitable_clearings
        return False, recruitable_clearings

    def is_battle_possible(self, board):
        battle_clearings = []
        for clearing in board.get_clearings_with_units(self.id):
            for token in board.graph.nodes[clearing]["tokens"]:
                if token["owner"] != self.id:
                    battle_clearings.append(clearing) if clearing not in battle_clearings else None
            for building in board.graph.nodes[clearing]["buildings"]:
                if building["owner"] != self.id and building["type"] != "ruins":
                    battle_clearings.append(clearing) if clearing not in battle_clearings else None
            if sum(units for owner, units in board.graph.nodes[clearing]["units"].items() if owner != self.id) > 0:
                battle_clearings.append(clearing) if clearing not in battle_clearings else None
                
        if battle_clearings:
            return True, battle_clearings
        return False, battle_clearings
    
    def is_move_possible(self, board):
        move_clearings = []
        controlled_clearings = board.get_controlled_clearings(self.id)
        clearings_with_units = board.get_clearings_with_units(self.id)
        
        for clearing in clearings_with_units:
            if clearing in controlled_clearings:
                for neighbor in board.get_adjacent_clearings(clearing):
                    move_clearings.append((clearing, neighbor))
            else:
                for neighbor in board.get_adjacent_clearings(clearing):
                    if neighbor in controlled_clearings:
                        move_clearings.append((clearing, neighbor))
        
        if move_clearings:
            return True, move_clearings
        return False, move_clearings
    
    def is_craft_possible(self, display, board, current_player, cards, items):
        objects    = cards.get_objects(current_player)
        craftables = cards.get_cratable_cards(current_player)
        usables = objects + craftables
        
        for clearing in board.get_clearings_with_crafters(self.id):
            self.builders[board.graph.nodes[clearing]["type"]] = board.get_number_of_crafters_for_a_clearing(clearing, self.id)
        
        # Check if the player can craft the item (Plus d'item = pas usable)

        valid_usables = []
        for card in usables:
            if card['cost_type'] == "none":
                if card['cost'] <= sum(self.builders.values()):
                    valid_usables.append(card)
            elif card['cost_type'] == "each":
                if all(self.builders[color] >= 1 for color in ["fox", "mouse", "rabbit"]):
                    valid_usables.append(card)
            elif card['cost'] <= self.builders.get(card['cost_type'], 0):
                valid_usables.append(card)
        return bool(valid_usables), valid_usables
    
    def get_possible_actions(self, board):
        raise NotImplementedError()
    
############################################################################################################
################################################# ACTIONS ##################################################
############################################################################################################    

    def recruit(self, display, board):
        is_possible, recruitable_clearings = self.is_recruitments_possible(board)
        if is_possible:
            if len(recruitable_clearings) > self.units:
                while self.units > 0:
                    recruit_clearing = display.ask_for_clearing(recruitable_clearings)
                    self.units -= 1
                    board.graph.nodes[recruit_clearing]["units"][self.id] += 1
            else:
                for r in recruitable_clearings:
                    self.units -= 1
                    board.graph.nodes[r]["units"][self.id] += 1
                                 
    def move(self, display, board, pass_available=False):
        # Rajouter gestion de l'achat du bateau
        
        # Récup from_clearing
        clearing_with_units = board.get_clearings_with_units(self.id)
        controled_clearings = board.get_controlled_clearings(self.id) 
        from_clearing = display.ask_for_clearing(clearing_with_units, pass_available)
        
        if from_clearing == "pass": return "pass"
        
        # Récup to_clearing
        adjacent_clearings = board.get_adjacent_clearings(from_clearing)
        adjacent_and_controlled_clearings = [clearing for clearing in adjacent_clearings if clearing in controled_clearings]
        if from_clearing not in controled_clearings:
            to_clearing = display.ask_for_clearing(adjacent_and_controlled_clearings, pass_available)
        else :
            to_clearing = display.ask_for_clearing(adjacent_clearings, pass_available)
        
        if to_clearing == "pass": return "pass"
        
        # Nb unités
        max_units = board.graph.nodes[from_clearing]["units"][self.id]
        if max_units > 1:
            units_to_move = display.ask_for_units_to_move(max_units, board.graph.nodes[to_clearing]["pos"])
        else:
            units_to_move = 1
            
        # Mise à jour des unités
        board.graph.nodes[from_clearing]["units"][self.id] -= units_to_move
        board.graph.nodes[to_clearing]["units"][self.id] = board.graph.nodes[to_clearing]["units"].get(self.id, 0) + units_to_move

        # Mise à jour du contrôle
        board.update_control(from_clearing)
        board.update_control(to_clearing)
        
    def battle(self, display, lobby, board, cards, pass_available=False):
    
        def _have_ennemy_things(clearing, thing, board):
            if thing == "units":
                return any(unit > 0 and faction_id != self.id for faction_id, unit in board.graph.nodes[clearing][thing].items())
            if thing == "buildings":
                return any(b["owner"] != self.id and b["owner"] != None for b in board.graph.nodes[clearing][thing])
            return any(t["owner"] != self.id for t in board.graph.nodes[clearing][thing])
        
        attackable_clearings = [clearing for clearing in board.graph.nodes if board.graph.nodes[clearing]["units"].get(self.id, 0) > 0 and any(_have_ennemy_things(clearing, thing, board) for thing in ["units", "buildings", "tokens"])]
        attack_clearing = display.ask_for_clearing(attackable_clearings, pass_available)
        
        if attack_clearing == "pass": return "pass"
        
        ennemy_factions = {faction_id for thing in ["units", "buildings", "tokens"]
                            for item in board.graph.nodes[attack_clearing][thing]
                            if (faction_id := (item if thing == "units" else item['owner'])) != self.id
                            and (thing != "units" or board.graph.nodes[attack_clearing]["units"].get(faction_id, 0) > 0)}
        ennemy_factions.discard(None)
        ennemy_factions = list(ennemy_factions)
                            
        # Get the ennemy faction
        defender_faction_id = ennemy_factions[0] if len(ennemy_factions) == 1 else display.ask_for_enemy(attack_clearing, ennemy_factions, pass_available)
        
        if defender_faction_id == "pass": return "pass"
                   
        # Gestion ambushes
        defender = lobby.get_player(defender_faction_id)
        attacker = lobby.get_player(lobby.current_player)
        ambush_cards_def = [card for card in defender.cards if card["type"] == "ambush" and (card["color"] == board.graph.nodes[attack_clearing]["type"] or card["color"] == "bird")]
        ambush_cards_att = [card for card in attacker.cards if card["type"] == "ambush" and (card["color"] == board.graph.nodes[attack_clearing]["type"] or card["color"] == "bird")]
        
        ambush_cards_def_id = [card['id'] for card in ambush_cards_def]
        ambush_cards_att_id = [card['id'] for card in ambush_cards_att]
        
        if ambush_cards_def and "Scouting Party" not in attacker.crafted_cards:
            lobby.current_player = lobby.get_player(defender.id)
            ambush_card_def = display.ask_for_cards(defender, criteria='id', values=ambush_cards_def_id, pass_available=True)
            lobby.current_player = lobby.get_player(attacker.id)
            
            # Si ambush defenseur
            if ambush_card_def != "pass": 
                defender.remove_card(ambush_card_def)
                
                # Si y'a une ambush attaquant pour contrer
                if ambush_cards_att != []:
                    ambush_card_att = display.ask_for_cards(attacker, criteria='id', values=ambush_cards_att_id, pass_available=True)
                    # Si il la joue
                    if ambush_card_att != "pass":
                        self.remove_card(ambush_card_att)
                        
                # Si pas d'ambush attaquant ou qu'il ne la joue pas
                if ambush_card_att == [] or ambush_card_att == "pass":
                    attacker_units = board.graph.nodes[attack_clearing]["units"].get(self.id, 0)
                    units_lost = min(2, attacker_units)
                    board.graph.nodes[attack_clearing]["units"][self.id] -= units_lost
                    self.units += units_lost
            if board.graph.nodes[attack_clearing]["units"].get(self.id, 0) == 0: return
                                                
        # Roll the dice
        dices =  [random.randint(0, 3), random.randint(0, 3)]
        attacker_roll, defender_roll = sorted(dices, reverse=defender_faction_id != 2)
                            
        # Calculate damage
        attacker_damage = min(attacker_roll, board.graph.nodes[attack_clearing]["units"].get(self.id, 0))
        defender_damage = min(defender_roll, board.graph.nodes[attack_clearing]["units"].get(defender_faction_id, 0))
                            
        # Si défenseur sans défense
        attacker_damage += 1 if board.graph.nodes[attack_clearing]["units"].get(defender_faction_id, 0) == 0 else 0
                     
        # TODO : Affichage les dommages et les dés
        display.battle_results = {
            "attack_clearing": attack_clearing,
            "attacker_roll": attacker_roll,
            "defender_roll": defender_roll,
            "attacker_damage": attacker_damage,
            "defender_damage": defender_damage
        }
        display.show_battle_results = True
        display.draw()
        pygame.display.flip() 
        pygame.time.delay(1000)
        
        # Gestion cartes de bataille défenseur
        att_effect = cards.get_battle_attacker_effect(attacker)
        def_effect = cards.get_battle_defender_effect(defender)
        
        att_effect_id = [card['id'] for card in att_effect]
        def_effect_id = [card['id'] for card in def_effect]
        
        while def_effect:
            lobby.current_player = defender.id
            card = display.ask_for_crafted_cards(defender, criteria='id', values=def_effect_id, pass_available=True)
            if card != "pass":
                defender.remove_crafted_card(card)
                
                if card['name'] == "Armorers" :
                    attacker_damage = 0
                    
                if card['name'] == "Sappers" :
                    defender_damage += 1
                    
                def_effect = cards.get_battle_defender_effect(defender)
            else : break
            
        lobby.current_player = self.id
        
        # Gestion cartes de bataille attaquant
        
        while att_effect:
            card = display.ask_for_crafted_cards(attacker, criteria='id', values=att_effect_id, pass_available=True)
            if card != "pass":
                attacker.remove_crafted_card(card)
                
                if card['name'] == "Armorers" :
                    defender_damage = 0
                    
                if card['name'] == "Brutal Tactics" :
                    attacker_damage += 1
                    lobby.get_player(defender_faction_id).points += 1
                    
                cards.get_battle_attacker_effect(attacker)
            else : break
            
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
        
        # Update display
        display.show_battle_results = False
        display.draw()
        pygame.display.flip()
        
        # Inflict damage               
        _inflict_damage(lobby, board, attack_clearing, defender_faction_id, attacker_damage)
        _inflict_damage(lobby, board, attack_clearing, self.id, defender_damage)
        
        # Update control
        board.update_control(attack_clearing)   
        
    def draw(self, display, current_player, cards):
        current_player.draw_cards(cards, self.number_card_draw_bonus + 1)
        while len(current_player.cards) > 5:
            card_selected = display.ask_for_cards(current_player)
            current_player.remove_card(card_selected)            

    def craft(self, display, board, current_player, cards, items):
        
        possible, craftable_cards = self.is_craft_possible(display, board, current_player, cards, items)
        
        while possible:
            craftable_cards_ids = [card['id'] for card in craftable_cards]
            card = display.ask_for_cards(current_player, criteria="id", values=craftable_cards_ids, pass_available=True)
            
            if card == "pass": break
            
            if card['type'] == "object":
                current_player.items[card['item']]  += 1
                items.available_items[card['item']] -= 1
                current_player.add_points(card['gain'])
                current_player.remove_card(card)
                self.builders[card['cost_type']] -= card['cost']
                
            elif "effect" in card['type']:
                current_player.crafted_cards.append(card)
                current_player.remove_card(card)
                self.builders[card['cost_type']] -= card['cost']
                
            elif card['type'] == "favor":
                points = 0
                for clearing in board.graph.nodes:
                    if board.graph.nodes[clearing]["type"] == card['color']:
                        points += len([building for building in board.graph.nodes[clearing]["buildings"] if building["owner"] != self.id])
                        points += len([token for token in board.graph.nodes[clearing]["tokens"] if token["owner"] != self.id])
                        board.graph.nodes[clearing]["buildings"] = [building for building in board.graph.nodes[clearing]["buildings"] if building["owner"] == self.id]
                        board.graph.nodes[clearing]["tokens"] = [token for token in board.graph.nodes[clearing]["tokens"] if token["owner"] == self.id]
                        if self.id in board.graph.nodes[clearing]["units"]:
                            board.graph.nodes[clearing]["units"] = {current_player.id: board.graph.nodes[clearing]["units"][self.id]}
                        else:
                            board.graph.nodes[clearing]["units"] = {}
                current_player.add_points(points)
                current_player.remove_card(card)
                self.builders[card['cost_type']] -= card['cost']

            possible, craftable_cards = self.is_craft_possible(display, board, current_player, cards, items)
            
            display.draw()
            pygame.display.flip()