from board import RootBoard
from display import RootDisplay

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

    display = RootDisplay(board)
    display.run()
    
    # Test de contrôle des clairières
    for node_id, node_data in board.graph.nodes(data=True):
        print(f"Clairière {node_id} contrôlée par : {node_data['control']}")