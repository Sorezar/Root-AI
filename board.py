import math
import networkx as nx
import json
import config

class RootBoard:
    def __init__(self, map_file):
        self.graph = nx.Graph()
        self.factions = {}
        self.rivers = []
        self.forests = {}
        self._load_map(map_file)

    def _load_map(self, map_file):
        try:
            with open(map_file, "r") as f:
                data = json.load(f)

            # Ajout des clairières et forêts (noeuds)
            for node in data["nodes"]:
                pos = (node["pos"][0] * config.BOARD_WIDTH, node["pos"][1] * config.BOARD_HEIGHT)
                self.graph.add_node(node["id"], 
                                    type=node["type"], 
                                    pos=pos, 
                                    control=None, 
                                    units={},
                                    slots=node.get("slots", 0),
                                    ruins=node.get("ruins", 0),
                                    tokens=node.get("tokens", []),
                                    buildings=[])
                
            # Ajout des ruines
            for node in data["nodes"]:
                if node.get("ruins", 0) > 0:
                    for _ in range(node["ruins"]):
                        self.graph.nodes[node["id"]]["buildings"].append({"type": "ruins", "owner": None})

                
            # Ajout des forêts
            for forest in data.get("forests", []):
                forest_id = forest["id"]
                adjacent_clearings = forest["adjacent_clearings"]
                
                # Calculer le centre de la forêt en faisant la moyenne des positions des clairières adjacentes
                x_sum = sum(self.graph.nodes[n]["pos"][0] for n in adjacent_clearings)
                y_sum = sum(self.graph.nodes[n]["pos"][1] for n in adjacent_clearings)
                center = (x_sum / len(adjacent_clearings), y_sum / len(adjacent_clearings))
                
                self.forests[forest_id] = {
                    "adjacent_clearings": adjacent_clearings,
                    "center": center,
                    "items": forest.get("items", [])
                }

            # Ajout des connexions (arêtes)
            for edge in data["edges"]:
                self.graph.add_edge(*edge)
                
            # Ajout des rivières
            for river in data["rivers"]:
                self.graph.add_edge(*river, is_river=True)
                self.rivers.append(tuple(river))

        except FileNotFoundError:
            print(f"Erreur : Le fichier {map_file} est introuvable.")
        except json.JSONDecodeError:
            print(f"Erreur : Le fichier {map_file} contient une erreur de format.")

    def get_forest_polygon_points(self, forest_id, shrink_factor=0.85):
        
        def _shrink_point(point, center, shrink_factor):
            dx = point[0] - center[0]
            dy = point[1] - center[1]
            new_x = center[0] + dx * shrink_factor
            new_y = center[1] + dy * shrink_factor
            return (new_x, new_y)
        
        forest = self.forests.get(forest_id)
        if not forest:
            return []
        points = [self.graph.nodes[n]["pos"] for n in forest["adjacent_clearings"]]
        center = forest["center"]
        points.sort(key=lambda p: math.atan2(p[1] - center[1], p[0] - center[0]))
        shrunk_points = [_shrink_point(p, center, shrink_factor) for p in points]
        
        return shrunk_points
    
    def get_nodes_and_edges(self):
        nodes  = [(n, self.graph.nodes[n]) for n in self.graph.nodes]
        edges  = [(u, v) for u, v, d in self.graph.edges(data=True) if not d.get('is_river', False)]
        rivers = [(u, v) for u, v, d in self.graph.edges(data=True) if d.get('is_river', False)]
        return nodes, edges, rivers, self.forests
    
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
            
    def get_adjacent_clearings(self, location):
        
        # Si on part d'une clairière
        if isinstance(location, int):
            if location not in self.graph:
                raise ValueError(f"Clairière {location} non trouvée")
            return list(self.graph.neighbors(location))
            
        # Si on part d'une forêt
        elif isinstance(location, str):
            if location not in self.forests:
                raise ValueError(f"Forêt {location} non trouvée")
            return self.forests[location]['adjacent_clearings']
            
        else:
            raise ValueError("La location doit être un ID de clairière (int) ou de forêt (str)")
    
    def get_adjacent_forests(self, clearing_id):
        if not isinstance(clearing_id, int):
            raise ValueError("L'ID de clairière doit être un entier")
            
        if clearing_id not in self.graph:
            raise ValueError(f"Clairière {clearing_id} non trouvée")
            
        adjacent_forests = []
        for forest_id, forest_data in self.forests.items():
            if clearing_id in forest_data['adjacent_clearings']:
                adjacent_forests.append(forest_id)
                
        return adjacent_forests
