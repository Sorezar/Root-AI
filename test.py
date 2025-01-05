class RootTest:
    def test_adjacency(self, board):
        print("\n=== Test des adjacences ===\n")
        
        # Test depuis une clairière
        clearing_id = 1
        print(f"Depuis la clairière {clearing_id}:")
        print(f"Clairières adjacentes: {board.get_adjacent_clearings(clearing_id)}")
        print(f"Forêts adjacentes: {board.get_adjacent_forests(clearing_id)}")
        
        # Test depuis une forêt
        forest_id = "F1"
        print(f"\nDepuis la forêt {forest_id}:")
        print(f"Clairières adjacentes: {board.get_adjacent_clearings(forest_id)}")
    
    def test_control(self, board):
        print("\n=== Test du contrôle des clairières ===\n")
        
        # Test de contrôle des clairières
        for node_id, node_data in board.graph.nodes(data=True):
            print(f"Clairière {node_id} contrôlée par : {node_data['control']}")
