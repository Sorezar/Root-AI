from board import RootBoard
from display import RootDisplay

def test_adjacency(board):
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
    
def test_control(board):
    print("\n=== Test du contrôle des clairières ===\n")
    
    # Test de contrôle des clairières
    for node_id, node_data in board.graph.nodes(data=True):
        print(f"Clairière {node_id} contrôlée par : {node_data['control']}")

if __name__ == "__main__":
    map_file = "maps/fall.json"
    board = RootBoard(map_file)

    # Ajout des factions
    board.add_faction("Marquise de Chat", (255, 165, 0))
    board.add_faction("Alliance", (0, 255, 0))

    # Placement d'unités
    board.place_unit("Marquise de Chat", 1)
    board.place_unit("Alliance", 2)
    board.place_unit("Marquise de Chat", 2)
    board.place_unit("Marquise de Chat", 2)
    board.place_unit("Alliance", 3)
    
    # Tests
    test_adjacency(board)
    test_control(board)

    display = RootDisplay(board)
    display.run()
    
    