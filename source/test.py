from specification import *
from game_map import Map
from algorithm import UCS_ghost, BFS_ghost, DFS_ghost, A_star_ghost
from map_implement import MapGraph
import os
import time
import colorama
from colorama import Fore, Back, Style

def test_algorithm(name, algorithm, graph, start_pos, target_pos):
    """Test pathfinding algorithm and display results"""
    print(f"Testing {name}...")
    start_time = time.time()
    
    # Updated to handle the third return value (next position)
    path, cost, next_pos = algorithm(graph, start_pos, target_pos)
    execution_time = time.time() - start_time
    
    if path:
        # Convert path to set of positions
        path_list = list(path)
        print(f"  Result: {len(path)} steps, total cost: {cost}")
        print(f"  Next position: {next_pos}")
        print(f"  Unique positions visited: {len(set(path_list))}")
        print(f"  Execution time: {execution_time:.6f} seconds")
    else:
        print("  No path found")
        path_list = []
    
    return path, cost, path_list, next_pos

def visualize_path_on_map(game_map, path, ghost_pos, player_pos, next_pos=None):
    """
    Visualize path on the map with colors
    """
    colorama.init()  # Initialize colorama
    
    # Create a copy of the map layout
    map_display = [list(row) for row in game_map.layout]
    
    # Define path set for faster lookup
    path_set = set(path)
    
    # Print the colored map
    print("\nPath Visualization:")
    
    for y, row in enumerate(map_display):
        line = ""
        for x, cell in enumerate(row):
            pos = (x, y)
            
            # Ghost position
            if pos == ghost_pos:
                line += Back.RED + 'G' + Style.RESET_ALL
            # Player position
            elif pos == player_pos:
                line += Back.GREEN + 'P' + Style.RESET_ALL
            # Next position
            elif pos == next_pos:
                line += Back.YELLOW + 'N' + Style.RESET_ALL
            # Path positions
            elif pos in path_set:
                line += Back.BLUE + cell + Style.RESET_ALL
            # Haunted points
            elif pos in game_map.haunted_points:
                line += Back.MAGENTA + cell + Style.RESET_ALL
            # Walls
            elif cell == '#':
                line += Back.WHITE + Fore.BLACK + '#' + Style.RESET_ALL
            # Regular cells
            else:
                line += cell
        print(line)
    
    # Print legend
    print("\nLegend:")
    print(Back.RED + 'G' + Style.RESET_ALL + " - Ghost")
    print(Back.GREEN + 'P' + Style.RESET_ALL + " - Player")
    print(Back.YELLOW + 'N' + Style.RESET_ALL + " - Next Position")
    print(Back.BLUE + '.' + Style.RESET_ALL + " - Path")
    print(Back.MAGENTA + '.' + Style.RESET_ALL + " - Haunted Point")
    print(Back.WHITE + Fore.BLACK + '#' + Style.RESET_ALL + " - Wall")

def test_interface():
    # Đơn giản hóa, chỉ load map và tạo graph
    test_map = Map.load_map(MAP_DIR)
    if not test_map:
        print("Error loading map!")
        exit(1)
    
    graph = MapGraph(test_map)
    print("Map loaded successfully")
    
    # Get positions
    try:
        ghost_pos = test_map.ghost_positions[ORANGE_GHOST]
    except:
        ghost_type = next(iter(test_map.ghost_positions))
        ghost_pos = test_map.ghost_positions[ghost_type]
        print(f"Using {ghost_type} ghost at {ghost_pos}")
    
    player_pos = test_map.player_pos
    
    print(f"Ghost: {ghost_pos}")
    print(f"Player: {player_pos}")
    
    # Danh sách các thuật toán để test
    algorithms = [
        ("UCS", UCS_ghost),
        ("BFS", BFS_ghost), 
        ("DFS", DFS_ghost),
        ("A*", A_star_ghost)
    ]
    
    # In kết quả dưới dạng bảng đơn giản
    print("\n" + "-" * 90)
    print(f"{'Algorithm':<8} {'Steps':<8} {'Total Cost':<12} {'Next Position':<15} {'Unique Positions'}")
    print("-" * 90)
    
    for name, algo in algorithms:
        # Reset graph state cho fair comparison
        if hasattr(graph, 'moves_since_haunted'):
            graph.moves_since_haunted = 0
        if hasattr(graph, 'haunted_points'):
            graph.haunted_points = set(test_map.haunted_points)
            
        path, cost, path_list, next_pos = test_algorithm(name, algo, graph, ghost_pos, player_pos)
        
        # Hiển thị kết quả trong bảng - chuyển next_pos thành chuỗi để tránh lỗi định dạng
        next_pos_str = str(next_pos) if next_pos else 'N/A'
        print(f"{name:<8} {len(path) if path else 'N/A':<8} {cost if cost else 'N/A':<12} {next_pos_str:<15} {len(set(path_list)) if path_list else 0}")
        
        # Visualize path on map with colors
        if path:
            visualize_path_on_map(test_map, path, ghost_pos, player_pos, next_pos)
            choice = input(f"\nPress Enter to continue to the next algorithm...")
    
    print("-" * 90)
    print("Test complete!")

if __name__ == "__main__":
    test_interface()