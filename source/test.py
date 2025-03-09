from specification import *
from game_map import Map
from algorithm import UCS_ghost, BFS_ghost, DFS_ghost, A_star_ghost
from map_implement import MapGraph
import time

def measure_pathfinding_time(algorithm, graph, start, target):
    """Measure execution time of pathfinding algorithm
    Args:
        algorithm: The pathfinding function to test
        graph: MapGraph instance
        start: Starting position (x,y)
        target: Target position (x,y)
    Returns:
        tuple: (path, cost, execution_time)
    """
    start_time = time.time()
    path, cost = algorithm(graph, start, target)
    end_time = time.time()
    return path, cost, end_time - start_time

if __name__ == "__main__":
    test_map = Map.load_map(MAP_DIR)
    map_graph = MapGraph(test_map)
    
    # Test positions
    ghost_pos = test_map.ghost_positions[ORANGE_GHOST]
    player_pos = test_map.player_pos

    # Test each algorithm
    algorithms = {
        "UCS": UCS_ghost,
        "BFS": BFS_ghost,
        "DFS": DFS_ghost,
        "A*": A_star_ghost
    }

    for name, algo in algorithms.items():
        path, cost, execution_time = measure_pathfinding_time(algo, map_graph, ghost_pos, player_pos)
        print(f"\n{name} Results:")
        print(f"Execution time: {execution_time:.4f} seconds")
        print(f"Path length: {len(path) if path else 'No path found'}")
        print(f"Total cost: {cost if cost else 'N/A'}")
