import networkx as nx
import json

class RootBoard:
    def __init__(self, map_file):
        self.graph = nx.Graph()
        self.factions = {}
        self.rivers = []
        self._load_map(map_file)

    def _load_map(self, map_file):
        try:
            with open(map_file, "r") as f:
                data = json.load(f)

            # Ajout des clairières (noeuds)
            for node in data["nodes"]:
                self.graph.add_node(node["id"], 
                                    type=node["type"], 
                                    pos=tuple(node["pos"]), 
                                    control=None, 
                                    units={})

            # Ajout des connexions (arêtes)
            for edge in data["edges"]:
                self.graph.add_edge(*edge)
                
            # Ajout des rivières
            for river in data["rivers"]:
                self.graph.add_edge(*river)
                self.rivers.append(tuple(river))

        except FileNotFoundError:
            print(f"Erreur : Le fichier {map_file} est introuvable.")
        except json.JSONDecodeError:
            print(f"Erreur : Le fichier {map_file} contient une erreur de format.")

    def add_faction(self, faction_name, color):
        self.factions[faction_name] = {"color": color, "units": 0}

    def place_unit(self, faction_name, clearing_id):
        if faction_name not in self.factions:
            print(f"Faction {faction_name} non trouvée.")
            return

        if clearing_id in self.graph.nodes:
            units = self.graph.nodes[clearing_id]["units"]
            units[faction_name] = units.get(faction_name, 0) + 1
            self.factions[faction_name]["units"] += 1
            self.update_control(clearing_id)
        else:
            print(f"Clairière {clearing_id} non trouvée.")

    def get_nodes_and_edges(self):
        nodes  = [(n, self.graph.nodes[n]) for n in self.graph.nodes]
        edges  = [(u, v) for u, v, d in self.graph.edges(data=True) if not d.get('is_river', False)]
        rivers = [(u, v) for u, v, d in self.graph.edges(data=True) if d.get('is_river', False)]
        return nodes, edges, rivers
    
    def update_control(self, clearing_id):
        units = self.graph.nodes[clearing_id]["units"]
        if units:
            max_units = max(units.values())
            controlling_factions = [faction for faction, count in units.items() if count == max_units]
            if len(controlling_factions) == 1:
                self.graph.nodes[clearing_id]["control"] = controlling_factions[0]
            else:
                self.graph.nodes[clearing_id]["control"] = None
        else:
            self.graph.nodes[clearing_id]["control"] = None

