from player import Player

class Lobby:
    def __init__(self):
        self.players = []
        self.current_player = 0
        self.available_factions = {
            0: 1,
            1: 1,
            2: 1,
            3: 2
        }

    def add_player(self, name, faction):
        if faction.id not in self.available_factions:
            raise ValueError(f"Faction {faction.name} inexistante.")

        if self.available_factions[faction.id] <= 0:
            raise ValueError(f"La faction {faction.name} est déjà prise.")
        
        player = Player(name, faction, id=len(self.players))
        self.players.append(player)
        self.available_factions[faction.id] -= 1
        return player

    def remove_player(self, name):
        for player in self.players:
            if player.name == name:
                self.available_factions[player.faction.id] += 1
                self.players.remove(player)
                return
        raise ValueError(f"Joueur {name} non trouvé.")

    def get_player(self, id):
        for player in self.players:
            if player.id == id:
                return player
        raise ValueError(f"Joueur {player.id} non trouvé.")

    def get_all_players(self):
        return self.players
    
    def get_scores(self):
        return {player.name: player.points for player in self.players}

    def get_current_player(self):
        return self.current_player
    