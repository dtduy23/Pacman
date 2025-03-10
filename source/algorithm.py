from specification import *
import heapq

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
    # Pure BFS implementation without considering weights during search
    queue = []
    # Start with all possible directions
    for direction in DIRECTIONS:
        queue.append((start_pos, direction, [start_pos]))
    
    # Track visited states (position, direction)
    visited = set()

    while queue:
        current_pos, current_dir, path = queue.pop(0)
        
        # Check if we reached the target
        if current_pos == target_pos:
            # Calculate cost after finding the path
            total_cost = calculate_path_cost(path, graph.haunted_points)
            return path, total_cost
        
        # Create state tuple (position, direction)
        state = (current_pos, current_dir)
        
        # Skip if we've already visited this state
        if state in visited:
            continue
            
        # Mark state as visited
        visited.add(state)
        
        # Get all valid neighbors (ignoring weights for BFS)
        neighbors = get_valid_neighbors(graph, current_pos, current_dir)
        
        # Add unvisited neighbors to queue
        for next_pos, next_dir in neighbors:
            next_state = (next_pos, next_dir)
            
            if next_state not in visited:
                new_path = path + [next_pos]
                queue.append((next_pos, next_dir, new_path))

    return None, None  # No path found

def get_valid_neighbors(graph, pos, direction):
    """
    Get valid neighbors without considering weights
    Returns list of (next_position, next_direction) pairs
    """
    neighbors = []
    
    # Get valid neighbors from graph
    neighbor_dict = graph.get_neighbors_with_weights((pos, direction))
    
    for next_pos in neighbor_dict:
        # Calculate direction from current to next position
        next_dir = (
            next_pos[0] - pos[0],
            next_pos[1] - pos[1]
        )
        neighbors.append((next_pos, next_dir))
    
    return neighbors

def calculate_path_cost(path, haunted_points):
    """
    Calculate the cost of a path after BFS has found it
    Applies rules:
    - STRAIGHT (2) for going straight
    - TURN (5) for 90 degree turns
    - BACK (10) for 180 degree turns
    - After haunted point, all movements cost STRAIGHT (2) for the next 20 steps
    """
    if len(path) <= 1:
        return 0
    
    total_cost = 0
    remaining_haunted_steps = 0
    
    # Track the previous direction - undefined for first step
    prev_dir = None
    
    for i in range(1, len(path)):
        # Get current and previous positions
        prev_pos = path[i-1]
        curr_pos = path[i]
        
        # Calculate current direction
        curr_dir = (curr_pos[0] - prev_pos[0], curr_pos[1] - prev_pos[1])
        
        # Check if at a haunted point
        if prev_pos in haunted_points:
            remaining_haunted_steps = HAUNTED_POINT_INDEX # Reset counter
        
        # Determine cost based on turn type and haunted status
        if remaining_haunted_steps > 0:
            # In haunted mode, all movements cost STRAIGHT
            cost = STRAIGHT
            remaining_haunted_steps -= 1
        else:
            # Normal mode - determine turn type based on previous direction
            if prev_dir is None:
                # First step has no turn
                cost = STRAIGHT
            else:
                # Determine turn type by comparing previous and current directions
                if prev_dir == curr_dir:
                    cost = STRAIGHT  # Going straight
                elif (prev_dir[0] == -curr_dir[0] and prev_dir[1] == -curr_dir[1]):
                    cost = BACK      # 180 degree turn
                else:
                    cost = TURN      # 90 degree turn
        
        # Store current direction for next iteration
        prev_dir = curr_dir
        
        total_cost += cost
    
    return total_cost

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
    # Pure DFS implementation without considering weights during search
    # Reset the haunted status counter
    graph.moves_since_haunted = 0
    
    # Stack for DFS, storing (position, direction, path)
    stack = []
    for direction in DIRECTIONS:
        stack.append((start_pos, direction, [start_pos]))
    
    # Track visited states (position, direction)
    visited = set()

    while stack:
        current_pos, current_dir, path = stack.pop()
        
        # Check if we reached the target
        if current_pos == target_pos:
            # Calculate cost after finding the path
            total_cost = calculate_path_cost(path, graph.haunted_points)
            return path, total_cost
        
        # Create state tuple (position, direction)
        state = (current_pos, current_dir)
        
        # Skip if we've already visited this state
        if state in visited:
            continue
            
        # Mark state as visited
        visited.add(state)
        
        # Get all valid neighbors (ignoring weights for DFS path finding)
        neighbors = get_valid_neighbors(graph, current_pos, current_dir)
        
        # Add unvisited neighbors to stack
        for next_pos, next_dir in neighbors:
            next_state = (next_pos, next_dir)
            
            if next_state not in visited:
                new_path = path + [next_pos]
                stack.append((next_pos, next_dir, new_path))

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
    # Sử dụng cách tiếp cận giống UCS
    # Reset the haunted status counter
    graph.moves_since_haunted = 0
    
    # Priority queue for A*, storing (f_score, g_score, position, direction, path)
    open_set = []
    for direction in DIRECTIONS:
        h_score = manhattan_distance(start_pos, target_pos)
        heapq.heappush(open_set, (
            h_score,  # f_score = g_score + h_score (g_score is 0 initially)
            0,        # g_score (cost so far)
            start_pos,
            direction,
            [start_pos]
        ))
    
    # Keep track of best costs to reach each state
    g_scores = {(start_pos, direction): 0 for direction in DIRECTIONS}
    
    # Keep track of visited states to avoid cycles
    closed_set = set()
    
    while open_set:
        f_score, g_score, current_pos, current_direction, path = heapq.heappop(open_set)
        
        # If we reached the target
        if current_pos == target_pos:
            # Option 1: Use the g_score (computed during search)
            # return path, g_score
            
            # Option 2: Recalculate cost using same method as BFS/DFS
            # This ensures consistency across all algorithms
            total_cost = calculate_path_cost(path, graph.haunted_points)
            return path, total_cost
        
        # Create a state tuple that includes position and direction
        state = (current_pos, current_direction)
        
        # Skip if we've already processed this state
        if state in closed_set:
            continue
            
        # Mark this state as processed
        closed_set.add(state)
        
        # Update haunted status when visiting a position
        # IMPORTANT: Either use update_haunted_status OR handle it in get_neighbors_with_weights
        # but not both (to avoid double counting)
        if current_pos in graph.haunted_points:
            graph.moves_since_haunted = 0  # Reset counter
        
        # Get neighbors with weights considering current direction
        neighbors = graph.get_neighbors_with_weights((current_pos, current_direction))
        
        for next_pos, weight in neighbors.items():
            # Calculate new direction from current to next position
            next_direction = (
                next_pos[0] - current_pos[0],
                next_pos[1] - current_pos[1]
            )
            
            # Create the next state
            next_state = (next_pos, next_direction)
            
            # Skip if we've already processed this state
            if next_state in closed_set:
                continue
            
            # Calculate new g_score (total cost to reach next_pos)
            new_g_score = g_score + weight
            
            # If we found a better path to this state or haven't seen it before
            if next_state not in g_scores or new_g_score < g_scores[next_state]:
                # Update the best cost to reach this state
                g_scores[next_state] = new_g_score
                
                # Create new path by appending next position
                new_path = path + [next_pos]
                
                # Calculate heuristic (Manhattan distance to target)
                h_score = manhattan_distance(next_pos, target_pos)
                
                # Calculate f_score = g_score + h_score
                new_f_score = new_g_score + h_score
                
                # Add to open set with updated scores
                heapq.heappush(open_set, (new_f_score, new_g_score, next_pos, next_direction, new_path))
    
    return None, None  # No path found