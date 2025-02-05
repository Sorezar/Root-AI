from factions.BaseFaction import Base
import random
import pygame

class Canopee(Base):
    def __init__(self):
        super().__init__("Dynastie de la Canopée", 1)
        self.scoring = {
            "roost":   [0, 1, 2, 3, 4, 4, 5]
        }
        self.buildings = {
            "roost": 7
        }
        self.units = 20
        self.decrees = {
            "recruit": [],
            "move": [],
            "battle": [],
            "build": []
        }

############################################################################################################
###################################### VERIFICATIONS ACTIONS POSSIBLES #####################################
############################################################################################################ 
    
    def is_recruit_possible(self, board, color_list):
        recruitable_clearings = []
        for clearing in board.graph.nodes:
            if ("bird" in color_list or board.graph.nodes[clearing]['type'] in color_list) and any(building['type'] == "roost" for building in board.graph.nodes[clearing]["buildings"]):
                recruitable_clearings.append(clearing)
                
        return bool(recruitable_clearings), recruitable_clearings
    
    def is_build_possible(self, board, color_list):
        buildable_clearings = []
        if self.buildings["roost"] > 0:
            for clearing in board.graph.nodes:
                if board.graph.nodes[clearing]["control"] == self.id:
                    if ("bird" in color_list or board.graph.nodes[clearing]['type'] in color_list):
                        if not any(building['type'] == "roost" for building in board.graph.nodes[clearing]["buildings"]):
                            buildable_clearings.append(clearing)
                            
        return bool(buildable_clearings), buildable_clearings
    
    def is_battle_possible(self, board, color_list):
        battle_clearings = []
        for clearing in board.get_clearings_with_units(self.id):
            clearing_type = board.graph.nodes[clearing]['type']
            if "bird" in color_list or clearing_type in color_list:
                for token in board.graph.nodes[clearing]["tokens"]:
                    if token["owner"] != self.id:
                        battle_clearings.append(clearing) if clearing not in battle_clearings else None
                for building in board.graph.nodes[clearing]["buildings"]:
                    if building["owner"] != self.id and building["type"] != "ruins":
                        battle_clearings.append(clearing) if clearing not in battle_clearings else None
                if sum(units for owner, units in board.graph.nodes[clearing]["units"].items() if owner != self.id) > 0:
                    battle_clearings.append(clearing) if clearing not in battle_clearings else None
                    
        return bool(battle_clearings), battle_clearings
    
    def is_move_possible(self, board, color_list):
        move_clearings = []
        controlled_clearings = board.get_controlled_clearings(self.id)
        clearings_with_units = board.get_clearings_with_units(self.id)
        
        for clearing in clearings_with_units:
            clearing_type = board.graph.nodes[clearing]['type']
            if "bird" in color_list or clearing_type in color_list:
                if clearing in controlled_clearings:
                    for neighbor in board.get_adjacent_clearings(clearing):
                        move_clearings.append((clearing, neighbor))
                else:
                    for neighbor in board.get_adjacent_clearings(clearing):
                        if neighbor in controlled_clearings:
                            move_clearings.append((clearing, neighbor))
        
        return bool(move_clearings), move_clearings
    
    def get_possible_action(self, board, current_decree, action):
        possible_action = []
        possible_clearings = []     
        for color in current_decree[action]:
            is_action_possible_method = getattr(self, f'is_{action}_possible')
            possible, clearings = is_action_possible_method(board, color)
            if possible:
                possible_action.append(color)
                possible_clearings += [clearing for clearing in clearings if clearing not in possible_clearings]
        
        return possible_action, possible_clearings
    
############################################################################################################
################################################# ACTIONS ##################################################
############################################################################################################

    def recruit(self, display, board, recruitable_clearings):
        recruit_clearing = display.ask_for_clearing(recruitable_clearings)
        self.units -= 1
        board.graph.nodes[recruit_clearing]["units"][self.id] += 1
        return board.graph.nodes[recruit_clearing]['type']
        
    def move(self, display, board, move_options):
        # Rajouter gestion de l'achat du bateau
        
        # Récup from_clearing et to_clearing
        from_clearing = display.ask_for_clearing([option[0] for option in move_options])
        to_clearing = display.ask_for_clearing([option[1] for option in move_options if option[0] == from_clearing])
        
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
        
        return board.graph.nodes[from_clearing]['type']
        
    def battle(self, display, lobby, board, cards, battle_clearings):
        
        attack_clearing = display.ask_for_clearing(battle_clearings)
        
        if attack_clearing == "pass": return "pass"
        
        ennemy_factions = {faction_id for thing in ["units", "buildings", "tokens"]
                            for item in board.graph.nodes[attack_clearing][thing]
                            if (faction_id := (item if thing == "units" else item['owner'])) != self.id
                            and (thing != "units" or board.graph.nodes[attack_clearing]["units"].get(faction_id, 0) > 0)}
        ennemy_factions.discard(None)
        ennemy_factions = list(ennemy_factions)
                            
        # Get the ennemy faction
        defender_faction_id = ennemy_factions[0] if len(ennemy_factions) == 1 else display.ask_for_enemy(attack_clearing, ennemy_factions)
        
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
        
        return board.graph.nodes[attack_clearing]['type']
        
    def build(self, display, board, build_clearings):
        clearing = display.ask_for_clearing(build_clearings)
        self.buildings['roost'] -= 1
        board.graph.nodes[clearing]["buildings"].append({"type": "roost", "owner": self.id})
    
        board.update_control(clearing)
        return board.graph.nodes[clearing]["type"]

############################################################################################################
############################################## GESTION DECRET ##############################################
############################################################################################################

    def resolve_decree(self, display, lobby, board, cards):
        current_decree = {action: colors.copy() for action, colors in self.decrees.items()}
        
        for action in ['recruit', 'move', 'battle', 'build']:
            while current_decree[action]:
                possible_actions, possible_clearings = self.get_possible_action(board, current_decree, action)
                if not possible_actions:
                    self.trigger_crisis(display, lobby)
                    return
                if action == 'battle':
                    color = self.battle(display, lobby, board, cards, possible_clearings)
                else:
                    color = getattr(self, action)(display, board, possible_clearings)
                current_decree[action].remove(color if color in current_decree[action] else "bird")
                
    def trigger_crisis(self, display, lobby):
        bird_cards = sum(color == "bird" for action in self.decrees.values() for color in action)
        self.points = max(0, lobby.players[lobby.current_player].points - bird_cards)
        self.decrees = {action: [] for action in self.decrees}
        
        # Afficher le message de crise
        display.draw_message("La Canopée tombe en crise !", duration=2000)
        
        # Choisir un nouveau leader (non implémenté ici)

############################################################################################################
############################################### TOUR DE JEU ################################################
############################################################################################################

    def birdsong_phase(self, current_player, display, cards, board):
        
        # 1 - Si main vide on pioche une carte
        if current_player.cards == []:
            current_player.cards.draw_cards(cards)
            
        # 2 - Add 1 or 2 cards to the decree
        for _ in range(2):
            selected_card = display.ask_for_cards(current_player, pass_available=(_ != 0))
            if selected_card == "pass": break
            
            action = display.ask_for_action_birds()
            self.decrees[action].append(selected_card["color"])
            current_player.remove_card(selected_card)
        
        # 3 - If no roosts, place a roost and 3 warriors in the clearing with the fewest total pieces
        if self.buildings["roost"] == 7:
            min_pieces = float('inf')
            target_clearings = []
            for clearing in board.graph.nodes:
                total_pieces = sum(units for owner, units in board.graph.nodes[clearing]["units"].items() if owner != self.id)
                total_pieces += len([building for building in board.graph.nodes[clearing]["buildings"] if building["owner"] != self.id])
                total_pieces += len([token for token in board.graph.nodes[clearing]["tokens"] if token["owner"] != self.id])
            
            if total_pieces < min_pieces:
                min_pieces = total_pieces
                target_clearings = [clearing]
            elif total_pieces == min_pieces:
                target_clearings.append(clearing)
            
            if target_clearings:
                if len(target_clearings) > 1:
                    target_clearing = display.ask_for_clearing(target_clearings)
                else:
                    target_clearing = target_clearings[0]
            
            board.graph.nodes[target_clearing]["buildings"].append({"type": "roost", "owner": self.id})
            board.graph.nodes[target_clearing]["units"][self.id] = board.graph.nodes[target_clearing]["units"].get(self.id, 0) + 3
            self.buildings["roost"] -= 1
            self.units -= 3
            board.update_control(target_clearing)
            
        
    def daylight_phase(self, display, lobby, board, cards, current_player, items):
        # 1 - Craft
        super().craft(display, board, current_player, cards, items)
        
        # 2 - Résolution du décret
        self.resolve_decree(display, lobby, board, cards)

    def evening_phase(self, display, current_player, cards):
        # Score points
        current_player.add_points(self.scoring["roost"][7 - self.buildings["roost"] - 1])
        
        # Draw a card
        self.draw(display, current_player, cards)
        
    def play(self, display, board, lobby, current_player, cards, items):
        self.birdsong_phase(current_player, display, cards, board)
        self.daylight_phase(display, lobby, board, cards, current_player, items)
        self.evening_phase(display, current_player, cards)
        