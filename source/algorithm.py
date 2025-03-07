from specification import *
import heapq

# def simulate_ghost_movement(game_map, path, costs, base_delay=0.1):
#     """
#     Simulate ghost movement with colors and variable delays based on movement costs
#     Args:
#         game_map: Map object containing the layout
#         path: List of positions for ghost to follow
#         costs: List of costs for each move
#         base_delay: Base delay time to multiply with costs
#     """
#     clear = lambda: os.system('cls')
#     map_state = [list(row) for row in game_map.layout]
    
#     # ANSI color codes
#     ORANGE = '\033[93m'
#     PATH = '\033[94m'
#     RESET = '\033[0m'
    
#     for i, pos in enumerate(path):
#         clear()
#         x, y = pos
        
#         if i > 0:
#             prev_x, prev_y = path[i-1]
#             map_state[prev_y][prev_x] = PATH + '*' + RESET
            
#         map_state[y][x] = ORANGE + 'O' + RESET
        
#         print(f"Step {i+1}/{len(path)}")
#         print(f"Current position: {pos}")
#         if i > 0:q
#             print(f"Move cost: {costs[i-1]}")
#             print(f"Delay: {costs[i-1] * base_delay:.2f} seconds")
#         for row in map_state:
#             print(''.join(row))
        
#         # Variable delay based on move cost
#         if i < len(path) - 1:
#             time.sleep(costs[i] * base_delay)

def UCS_ghost(graph, start_pos, target_pos):
    """
    Uniform Cost Search algorithm for orange ghost to find path to player
    Args:
        graph: MapGraph object containing the game map
        start_pos: Starting position of orange ghost (x,y)
        target_pos: Target position (Pacman's position) (x,y)
    Returns:
        path: List of positions from ghost to player
        cost: Total cost of the path
    """
    # Priority queue stores: (total_cost, current_pos, prev_direction, path)
    frontier = []
    # Start with all possible directions
    for direction in DIRECTIONS:
        heapq.heappush(frontier, (0, start_pos, direction, [start_pos]))
    
    # Keep track of visited states (position, coming_from_direction)
    visited = set()
    
    while frontier:
        total_cost, current_pos, prev_direction, path = heapq.heappop(frontier)
        
        # Check if reached target
        if current_pos == target_pos:
            return path, total_cost
            
        # Get state identifier
        state = (current_pos, prev_direction)
        if state in visited:
            continue
            
        visited.add(state)
        
        # Get neighbors with weights from current position and direction
        neighbors = graph.get_neighbors_with_weights((current_pos, prev_direction))
        
        # Add neighbors to frontier
        for next_pos, weight in neighbors.items():
            if (next_pos, prev_direction) not in visited:
                new_cost = total_cost + weight
                new_path = path + [next_pos]
                heapq.heappush(frontier, (new_cost, next_pos, prev_direction, new_path))
    
    return None, None  # No path found

# # Test code
# if __name__ == "__main__":
#     # Load map and create graph
#     game_map = Map.load_map(MAP_DIR)
#     if game_map is None:
#         print("Error: Could not load map file")
#         exit(1)
        
#     map_graph = MapGraph(game_map)
    
#     # Get positions
#     ghost_pos = map_graph.positions['ghosts']['orange']
#     player_pos = map_graph.positions['player']
    
#     # Find path using UCS
#     path, cost = UCS_ghost(map_graph, ghost_pos, player_pos)
    
#     if path:
#         print("\nOrange Ghost to Pacman path found!")
#         print(f"Starting position: {ghost_pos}")
#         print(f"Target position: {player_pos}")
#         print(f"Path: {' -> '.join(str(pos) for pos in path)}")
#         print(f"Total cost: {cost}")
        
#         # Calculate costs for each move
#         move_costs = []
#         for i in range(len(path)-1):
#             pos = path[i]
#             next_pos = path[i+1]
#             for direction in DIRECTIONS:
#                 neighbors = map_graph.get_neighbors_with_weights((pos, direction))
#                 if next_pos in neighbors:
#                     move_costs.append(neighbors[next_pos])
#                     break
        
#         # Ask user if they want to see the simulation
#         input("\nPress Enter to start movement simulation...")
#         simulate_ghost_movement(game_map, path, move_costs)
#     else:
#         print("No path found!")
