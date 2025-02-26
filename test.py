class RootTest:
    def test_adjacency(self, board):
        print("\n=== Test des adjacences ===\n")
        
        # Test depuis une clairière
        for clearing in board.graph.nodes :
            print(f"Depuis la clairière {clearing}:")
            print(f"Clairières adjacentes: {board.get_adjacent_clearings(clearing)}")
            print(f"Forêts adjacentes: {board.get_adjacent_forests(clearing)}")
        
        print("Si loutres")
        
        # Test depuis une clairière
        for clearing in board.graph.nodes :
            print(f"Depuis la clairière {clearing}:")
            print(f"Clairières adjacentes: {board.get_adjacent_clearings_through_river(clearing)}")
            print(f"Forêts adjacentes: {board.get_adjacent_forests(clearing)}")
        
        # Test depuis une forêt
        forest_id = "F1"
        print(f"\nDepuis la forêt {forest_id}:")
        print(f"Clairières adjacentes: {board.get_adjacent_clearings(forest_id)}")
    
    def test_control(self, board):
        print("\n=== Test du contrôle des clairières ===\n")
        
        # Test de contrôle des clairières
        for node_id, node_data in board.graph.nodes(data=True):
            print(f"Clairière {node_id} contrôlée par : {node_data['control']}")

    def test_units(self, board, lobby):
        print("\n=== Test du placement des unités ===\n")
        
        # Test du placement des unités
        for node_id, node_data in board.graph.nodes(data=True):
            print(f"Clairière {node_id} : {node_data['units']}")
            
        for player in lobby.players:
            print(f"Joueur {player.id} : {player.faction.units}")
            
    def test_tokens(self, board):
        print("\n=== Test du placement des tokens ===\n")
        
        # Test du placement des tokens
        for node_id, node_data in board.graph.nodes(data=True):
            print(f"Clairière {node_id} : {node_data['tokens']}")
    
    def test_buildings(self, board):
        print("\n=== Test du placement des bâtiments ===\n")
        
        # Test du placement des bâtiments
        for node_id, node_data in board.graph.nodes(data=True):
            print(f"Clairière {node_id} : {node_data['buildings']}")