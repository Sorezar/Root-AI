class RootTest:
    def test_adjacency(self, board):
        print("\n=== Test des adjacences ===\n")
        
        # Test depuis une clairière
        for clearing in board.graph.nodes :
            print(f"Depuis la clairière {clearing}:")
            print(f"Clairières adjacentes: {board.get_adjacent_clearings(clearing)}")
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

    def test_units(self, board):
        print("\n=== Test du placement des unités ===\n")
        
        # Test du placement des unités
        for node_id, node_data in board.graph.nodes(data=True):
            print(f"Clairière {node_id} : {node_data['units']}")