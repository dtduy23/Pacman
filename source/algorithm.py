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
        target_pos: Target position (Pacman's position)
    Returns:
        the list of positions from ghost to player
        the total cost of the path
    """
    # Reset the haunted status counter
    graph.moves_since_haunted = 0
    
    frontier = []
    for direction in DIRECTIONS:
        heapq.heappush(frontier, (0, start_pos, direction, [start_pos]))
    
    visited = set()
    cost_so_far = {(start_pos, direction): 0 for direction in DIRECTIONS}  # Track minimum costs
    
    while frontier:
        total_cost, current_pos, prev_direction, path = heapq.heappop(frontier)
        
        if current_pos == target_pos:
            return path, total_cost
            
        state = (current_pos, prev_direction)
        if state in visited:
            continue
            
        visited.add(state)
        
        # Update haunted status when visiting a position
        graph.update_haunted_status(current_pos)
        
        neighbors = graph.get_neighbors_with_weights((current_pos, prev_direction))
        
        for next_pos, weight in neighbors.items():
            # Calculate new direction
            next_direction = (
                next_pos[0] - current_pos[0],
                next_pos[1] - current_pos[1]
            )
            next_state = (next_pos, next_direction)
            new_cost = total_cost + weight
            
            if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
                cost_so_far[next_state] = new_cost
                new_path = path + [next_pos]
                heapq.heappush(frontier, (new_cost, next_pos, next_direction, new_path))
    
    return None, None


def BFS_ghost(graph, start_pos, target_pos):
    """
    Breadth First Search algorithm for orange ghost to find path to player
    Args:
        graph: MapGraph object containing the game map
        start_pos: Starting position of orange ghost (x,y)
        target_pos: Target position (Pacman's position)
    Returns:
        the list of positions from ghost to player
        the total cost of the path
    """
    # Queue for BFS, storing (position, path, total_cost)
    queue = [(start_pos, [start_pos], 0)]
    visited = set([start_pos])  # Track visited positions

    while queue:
        current_pos, path, total_cost = queue.pop(0)
        
        if current_pos == target_pos:
            return path, total_cost
        
        # Get neighbors with weights from current position
        # Use any direction since BFS doesn't care about coming direction
        neighbors = graph.get_neighbors_with_weights((current_pos, DIRECTIONS[0]))
        
        # Add unvisited neighbors to queue
        for next_pos, weight in neighbors.items():
            if next_pos not in visited:
                visited.add(next_pos)  # Mark as visited immediately
                new_path = path + [next_pos]
                new_cost = total_cost + weight
                queue.append((next_pos, new_path, new_cost))

    return None, None  # No path found

def DFS_ghost(graph, start_pos, target_pos):
    """
    Depth First Search algorithm for orange ghost to find path to player
    Args:
        graph: MapGraph object containing the game map
        start_pos: Starting position of orange ghost (x,y)
        target_pos: Target position (Pacman's position)
    Returns:
        the list of positions from ghost to player
        the total cost of the path
    """
    # Stack for DFS, storing (position, path, total_cost)
    stack = [(start_pos, [start_pos], 0)]
    visited = set()

    while stack:
        current_pos, path, total_cost = stack.pop()
        
        if current_pos == target_pos:
            return path, total_cost
            
        if current_pos in visited:
            continue
            
        visited.add(current_pos)
        
        # Get neighbors with weights from current position
        # Use any direction since DFS doesn't care about coming direction
        neighbors = graph.get_neighbors_with_weights((current_pos, DIRECTIONS[0]))
        
        for next_pos, weight in neighbors.items():
            if next_pos not in visited:
                new_path = path + [next_pos]
                new_cost = total_cost + weight
                stack.append((next_pos, new_path, new_cost))

    return None, None  # No path found

def manhattan_distance(pos1, pos2):
    """Calculate Manhattan distance between two points"""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def A_star_ghost(graph, start_pos, target_pos):
    """
    A* Search algorithm for orange ghost to find path to player
    Args:
        graph: MapGraph object containing the game map
        start_pos: Starting position of orange ghost (x,y)
        target_pos: Target position (Pacman's position)
    Returns:
        the list of positions from ghost to player
        the total cost of the path
    """
    # Reset the haunted status counter
    graph.moves_since_haunted = 0
    
    # Priority queue for A*, storing (f_score, g_score, position, direction, path)
    open_set = []
    for direction in DIRECTIONS:
        heapq.heappush(open_set, (
            manhattan_distance(start_pos, target_pos),  # f_score = g_score + h_score
            0,  # g_score (cost so far)
            start_pos,
            direction,
            [start_pos]
        ))
    
    # Keep track of visited states and their costs
    visited = set()
    g_scores = {(start_pos, direction): 0 for direction in DIRECTIONS}
    
    while open_set:
        f_score, g_score, current_pos, prev_direction, path = heapq.heappop(open_set)
        
        # If we reached the target
        if current_pos == target_pos:
            return path, g_score
        
        state = (current_pos, prev_direction)
        if state in visited:
            continue
            
        visited.add(state)
        
        # Update haunted status when visiting a position
        graph.update_haunted_status(current_pos)
        
        # Get neighbors with weights considering haunted points
        neighbors = graph.get_neighbors_with_weights((current_pos, prev_direction))
        
        for next_pos, weight in neighbors.items():
            # Calculate new g_score
            new_g_score = g_score + weight
            
            # Calculate new state
            next_direction = (
                next_pos[0] - current_pos[0],
                next_pos[1] - current_pos[1]
            )
            next_state = (next_pos, next_direction)
            
            # If we found a better path to this state
            if next_state not in g_scores or new_g_score < g_scores[next_state]:
                g_scores[next_state] = new_g_score
                new_path = path + [next_pos]
                
                # Calculate f_score = g_score + h_score
                f_score = new_g_score + manhattan_distance(next_pos, target_pos)
                
                heapq.heappush(open_set, (f_score, new_g_score, next_pos, next_direction, new_path))
    
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
