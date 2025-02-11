import random

class Cards:
    def __init__(self, deck):
        self.deck = deck
        self.discard = []
        self.quests = []
        
    def draw(self, number=1):
        cards = []
        for _ in range(number):
            if not self.deck:
                self.deck = self.discard
                self.discard = []
                self.shuffle()
            cards.append(self.deck.pop())
        return cards
        
    def shuffle(self):
        random.shuffle(self.deck)
        
############################################################################################################
########################################### FONCTION DES CARTES ############################################
############################################################################################################

    ################################################
    # CRAFT : Cartes de craft d'objets et/ou effet #
    ################################################
    
    def get_objects(self, current_player):
        return [card for card in current_player.cards if card["type"] == "object"]
    
    def get_cratable_cards(self, current_player):
        return [card for card in current_player.cards if "effect" in card["type"] or card["type"] == "favor"]
    
    ############################################
    # EFFETS : Cartes craftée qui ont un effet #
    ############################################

    ## EFFETS DE DEBUT DE PHASE
    def get_start_birdsong_effect(self, current_player):
        return [card for card in current_player.crafted_cards if card["type"] == "start_birdsong_effect" or card["type"] == "dominance"]
    def get_start_daylight_effect(self, current_player):
        return [card for card in current_player.crafted_cards if card["type"] == "start_daylight_effect"]
    def get_start_evening_effect(self, current_player):
        return [card for card in current_player.crafted_cards if card["type"] == "start_evening_effect"]

    ## EFFET A N'IMPORTE QUEL MOMENT DE LA PHASE DE JEU
    def get_birdsong_effect(self, current_player):
        return [card for card in current_player.crafted_cards if card["type"] == "birdsong_effect"]
    def get_daylight_effect(self, current_player):
        return [card for card in current_player.crafted_cards if card["type"] == "daylight_effect"]
    def get_evening_effect(self, current_player):
        return [card for card in current_player.crafted_cards if card["type"] == "evening_effect"]
    
    ## EFFET DE BATAILLE
    
    ### Effets en tant qu'attaquant
    def get_battle_attacker_effect(self, current_player):
        return [card for card in current_player.crafted_cards if card["type"] == "battle_attacker_effect" or card["type"] == "battle_effect"]
    
    ### Effets en tant que défenseur
    def get_battle_defender_effect(self, current_player):
        return [card for card in current_player.crafted_cards if card["type"] == "battle_defender_effect" or card["type"] == "battle_effect"]
    
    ###########################################################
    # ACTIFS : Cartes qui ont un effect actif à l'utilisation #
    ###########################################################
    
    ## ACTIFS DE DEBUT DE PHASE
    def get_start_birdsong_active(self, current_player):
        return [card for card in current_player.cards if card["type"] == "start_birdsong_active"]
    def get_start_daylight_active(self, current_player):
        return [card for card in current_player.cards if card["type"] == "start_daylight_active"]
    def get_start_evening_active(self, current_player):
        return [card for card in current_player.cards if card["type"] == "start_evening_active"]
    
    ## ACTIFS A N'IMPORTE QUEL MOMENT DE LA PHASE DE JEU
    
    def get_birdsong_active(self, current_player):
        return [card for card in current_player.cards if card["type"] == "birdsong_active"]
    def get_daylight_active(self, current_player):
        return [card for card in current_player.cards if card["type"] == "daylight_active"]
    def get_evening_active(self, current_player):
        return [card for card in current_player.cards if card["type"] == "evening_active"]
    
    ## ACTIFS DE BATAILLE
    
    ### Actifs en tant qu'attaquant
    def get_battle_attacker_active(self, current_player):
        return [card for card in current_player.cards if card["type"] == "battle_attacker_active"]
    
    ### Actifs en tant que défenseur
    def get_battle_defender_active(self, current_player):
        return [card for card in current_player.cards if card["type"] == "battle_defender_active" or card["type"] == "ambush"]

############################################################################################################
########################################### FONCTION DES PHASES ############################################
############################################################################################################

    #TODO : Filrer les effets jouables en fonction de leur effet (ex : Command Warren que si is_battle_possible)

    # BIRDSONG
    def resolve_start_birdsong_effect(self, current_player, lobby, board, display):
        start_birdsong_effects = self.get_start_birdsong_effect(current_player)
        if not len(start_birdsong_effects) > 0 : return
        card = display.ask_for_crafted_cards(current_player, criteria='id', values=[card['id'] for card in start_birdsong_effects], pass_available=True)
        
        if card == "pass":
            return
        
        if card['name'] == "Better Burrow Bank":
            players = [player for player in lobby.players if player.id != current_player.id]
            player = display.ask_for_players(players)
            current_player.append(self.draw())
            player.append(self.draw())
            
    def resolve_birdsong_effect(self, current_player, lobby, board, display):
        birdsong_effects = self.get_birdsong_effect(current_player)
        if not len(birdsong_effects) > 0 : return
        card = display.ask_for_crafted_cards(current_player, criteria='id', values=[card['id'] for card in birdsong_effects], pass_available=True)
        
        if card == "pass":
            return
        
        if card['name'] == "Royal Claim":
            clearings_controlled = board.get_controlled_clearings(current_player.id)
            current_player.points += len(clearings_controlled)
            current_player.crafted_cards.remove(card)
            self.discard.append(card)
            
        if card['name'] == "Stand and Deliver":
            players = [player for player in lobby.players if player.id != current_player.id and len(player.cards) > 0]
            player = display.ask_for_players(lobby.players)
            if player.cards:
                stolen_card = random.choice(player.cards)
                player.cards.remove(stolen_card)
                current_player.cards.append(stolen_card)
                player.points += 1
    
    # DAYLIGHT
    def resolve_start_daylight_effect(self, current_player, lobby, board, display):
        start_daylight_effects = self.get_start_daylight_effect(current_player)
        if not len(start_daylight_effects) > 0 : return
        card = display.ask_for_crafted_cards(current_player, criteria='id', values=[card['id'] for card in start_daylight_effects], pass_available=True)
        
        if card == "pass":
            return
        
        if card['name'] == "Command Warren":
            current_player.faction.battle(display, board, lobby)
            
    def resolve_daylight_effect(self, current_player, lobby, board, display):
        daylight_effects = self.get_daylight_effect(current_player)
        if not len(daylight_effects) > 0 : return
        card = display.ask_for_crafted_cards(current_player, criteria='id', values=[card['id'] for card in daylight_effects], pass_available=True)
        
        if card == "pass":
            return

        if card['name'] == "Tax Collector":
            clearing = display.ask_for_clearings(board.get_clearings_with_units(current_player.id))
            board.graph.nodes[clearing]["units"][current_player.id] -= 1
            current_player.cards.append(self.draw())
              
        # TODO : Ajouter un moyen pour le joueur de stocker les cartes connus (pour l'IA)
        if card['name'] == "Codebreakers":
            player = display.ask_for_players(lobby.players)
            display.show_player_cards(player)
            
    # EVENING
    def resolve_start_evening_effect(self, current_player, lobby, board, display):
        start_evening_effects = self.get_start_evening_effect(current_player)
        if not len(start_evening_effects) > 0: return
        card = display.ask_for_crafted_cards(current_player, criteria='id', values=[card['id'] for card in start_evening_effects], pass_available=True)
        
        if card == "pass":
            return
        
        # TODO : Vérifier avant s'il peut bouger
        if card['name'] == "Cobbler":
            current_player.faction.move(display, board)
            
    def resolve_evening_effect(self, current_player, lobby, board, display):
        # Pour l'instant pas de cartes jouables en soirée
        return
        
        evening_effects = self.get_evening_effect(current_player)
        if not len(evening_effects) > 0: return
        card = display.ask_for_crafted_cards(current_player, criteria='id', values=[card['id'] for card in evening_effects], pass_available=True)
        
        if card == "pass":
            return