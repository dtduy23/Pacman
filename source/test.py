from specification import *
from game_map import Map
from algorithm import UCS_ghost, BFS_ghost, DFS_ghost, A_star_ghost
from map_implement import MapGraph
import time
import os

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

def visualize_path(game_map, path, ghost_pos, player_pos, haunted_points):
    """
    Visualize the path found by the algorithm on the map
    Args:
        game_map: Map object containing the layout
        path: List of positions for ghost to follow
        ghost_pos: Starting position of the ghost
        player_pos: Position of the player
        haunted_points: List of haunted points
    """
    if not path:
        print("No path to visualize!")
        return

    # Create a copy of the map layout
    map_display = [list(row) for row in game_map.layout]
    
    # Mark the path with numbers
    for i, pos in enumerate(path[1:-1], 1):  # Skip start and end positions
        x, y = pos
        # Use modulo to cycle through single digits for better readability
        map_display[y][x] = str(i % 10)
    
    # Mark haunted points
    for x, y in haunted_points:
        if (x, y) not in [ghost_pos, player_pos] and (x, y) not in path[1:-1]:
            map_display[y][x] = 'H'
    
    # Mark ghost position
    gx, gy = ghost_pos
    map_display[gy][gx] = 'G'
    
    # Mark player position
    px, py = player_pos
    map_display[py][px] = 'P'
    
    # Print the map with the path
    print("\nPath Visualization:")
    print("G: Ghost starting position")
    print("P: Player position")
    print("H: Haunted points")
    print("Numbers: Path sequence")
    print("-" * (len(map_display[0]) + 2))
    
    for row in map_display:
        print("|" + "".join(row) + "|")
    
    print("-" * (len(map_display[0]) + 2))

def print_path_details(path, cost):
    """
    Print detailed information about the path
    Args:
        path: List of positions
        cost: Total cost of the path
    """
    if not path:
        print("No path found!")
        return
    
    print("\nDetailed Path:")
    print(f"Total steps: {len(path) - 1}")
    print(f"Total cost: {cost}")
    
    print("\nStep-by-step path:")
    for i in range(len(path) - 1):
        current = path[i]
        next_pos = path[i+1]
        
        # Calculate direction
        dx = next_pos[0] - current[0]
        dy = next_pos[1] - current[1]
        
        # Determine direction name
        direction = ""
        if dx == 1: direction = "RIGHT"
        elif dx == -1: direction = "LEFT"
        elif dy == 1: direction = "DOWN"
        elif dy == -1: direction = "UP"
        
        print(f"Step {i+1}: Move from {current} to {next_pos} ({direction})")

if __name__ == "__main__":
    test_map = Map.load_map(MAP_DIR)
    map_graph = MapGraph(test_map)
    
    # Test positions
    ghost_pos = test_map.ghost_positions[ORANGE_GHOST]
    player_pos = test_map.player_pos
    haunted_points = test_map.haunted_points

    # Test each algorithm
    algorithms = {
        # "UCS": UCS_ghost,
        # "BFS": BFS_ghost,
        # "DFS": DFS_ghost,
        "A*": A_star_ghost
    }

    for name, algo in algorithms.items():
        print(f"\n{'=' * 50}")
        print(f"Testing {name} Algorithm")
        print(f"{'=' * 50}")
        
        path, cost, execution_time = measure_pathfinding_time(algo, map_graph, ghost_pos, player_pos)
        
        print(f"\n{name} Results:")
        print(f"Execution time: {execution_time:.4f} seconds")
        print(f"Path length: {len(path) if path else 'No path found'}")
        print(f"Total cost: {cost if cost else 'N/A'}")
        
        # Visualize the path
        visualize_path(test_map, path, ghost_pos, player_pos, haunted_points)
        
        # Print detailed path information
        # print_path_details(path, cost)
        
        # Wait for user input before showing next algorithm
        input("\nPress Enter to continue to the next algorithm...")
        os.system('cls' if os.name == 'nt' else 'clear')