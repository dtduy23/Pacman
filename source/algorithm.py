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
        the next position for the ghost to move to (first step)
    """
    # Reset the haunted status counter - using a copy to avoid affecting other algorithms
    original_haunted_points = set(graph.haunted_points)
    moves_since_haunted = 0
    
    frontier = []
    for direction in DIRECTIONS:
        heapq.heappush(frontier, (0, start_pos, direction, [start_pos]))
    
    visited = set()
    cost_so_far = {(start_pos, direction): 0 for direction in DIRECTIONS}  # Track minimum costs
    
    # Dictionary to track haunted steps for each path
    haunted_steps = {(start_pos, direction): 0 for direction in DIRECTIONS}
    
    while frontier:
        total_cost, current_pos, prev_direction, path = heapq.heappop(frontier)
        
        if current_pos == target_pos:
            # Recalculate the cost using the same function as BFS/DFS
            # to ensure consistency between algorithms
            final_cost = calculate_path_cost(path, original_haunted_points)
            
            # Return the next position if path has more than one position
            next_pos = path[1] if len(path) > 1 else start_pos
            return path, final_cost, next_pos
            
        state = (current_pos, prev_direction)
        if state in visited:
            continue
            
        visited.add(state)
        
        # Update haunted status for THIS path
        current_haunted_steps = haunted_steps[state]
        if current_pos in original_haunted_points:
            current_haunted_steps = 0  # Reset counter when on haunted point
        
        # Get neighbors with calculated weights
        neighbors = {}
        raw_neighbors = graph.graph.get((current_pos, prev_direction), {})
        
        for next_pos, base_weight in raw_neighbors.items():
            # Apply haunted rule if applicable
            if current_haunted_steps < HAUNTED_POINT_INDEX:
                # In haunted mode, all movements cost STRAIGHT
                weight = STRAIGHT
            else:
                # Normal mode - use original weight
                weight = base_weight
                
            neighbors[next_pos] = weight
        
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
                
                # Update haunted steps for next state
                haunted_steps[next_state] = current_haunted_steps + 1
                
                heapq.heappush(frontier, (new_cost, next_pos, next_direction, new_path))
    
    return None, None, None


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
        the next position for the ghost to move to (first step)
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
            
            # Return the next position if path has more than one position
            next_pos = path[1] if len(path) > 1 else start_pos
            return path, total_cost, next_pos
        
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

    return None, None, None  # No path found

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
        the next position for the ghost to move to (first step)
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
            
            # Return the next position if path has more than one position
            next_pos = path[1] if len(path) > 1 else start_pos
            return path, total_cost, next_pos
        
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

    return None, None, None  # No path found

def manhattan_distance(pos1, pos2):
    """Calculate Manhattan distance between two points"""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def A_star_ghost(graph, start_pos, target_pos):
    """
    Optimized A* Search algorithm for ghost pathfinding
    Args:
        graph: MapGraph object containing the game map
        start_pos: Starting position of ghost (x,y)
        target_pos: Target position (Pacman's position)
    Returns:
        the list of positions from ghost to player
        the total cost of the path
        the next position for the ghost to move to (first step)
    """
    # Create a local copy of haunted points to avoid affecting other algorithms
    original_haunted_points = set(graph.haunted_points)
    
    # Cache for heuristic calculations to avoid redundant calculations
    heuristic_cache = {}
    
    # Dictionary to track haunted state for each path independently
    haunted_steps = {}
    
    # More efficient priority queue initialization
    open_set = []
    g_scores = {}
    f_scores = {}
    came_from = {}  # For efficient path reconstruction
    
    # Initialize starting nodes for all possible directions
    for direction in DIRECTIONS:
        state = (start_pos, direction)
        g_scores[state] = 0
        f_scores[state] = get_heuristic(start_pos, target_pos, heuristic_cache)
        haunted_steps[state] = 0
        heapq.heappush(open_set, (f_scores[state], 0, id(state), state, [start_pos]))  # Using id() to break ties
    
    # Set to track closed states
    closed_set = set()
    
    # Counter for tie-breaking when f_scores are equal
    counter = 0
    
    while open_set:
        # Extract state with lowest f_score
        _, _, _, current_state, path = heapq.heappop(open_set)
        current_pos, current_direction = current_state
        
        # Goal test
        if current_pos == target_pos:
            # Calculate final cost using consistent method
            total_cost = calculate_path_cost(path, original_haunted_points)
            
            # Get next position for ghost movement
            next_pos = path[1] if len(path) > 1 else current_pos
            return path, total_cost, next_pos
        
        # Skip if already processed
        if current_state in closed_set:
            continue
        
        # Add to closed set
        closed_set.add(current_state)
        
        # Get current haunted state for this path
        current_haunted_steps = haunted_steps[current_state]
        
        # Check if position is a haunted point
        if current_pos in original_haunted_points:
            current_haunted_steps = 0  # Reset counter
        
        # Get neighbors with weights
        neighbors = {}
        raw_neighbors = graph.graph.get(current_state, {})
        
        # Apply haunted effect to movement costs if applicable
        for next_pos, base_weight in raw_neighbors.items():
            # Apply haunted rule if applicable
            weight = STRAIGHT if current_haunted_steps < HAUNTED_POINT_INDEX else base_weight
            neighbors[next_pos] = weight
        
        # Process neighbors
        for next_pos, weight in neighbors.items():
            # Calculate direction to next position
            next_direction = (next_pos[0] - current_pos[0], next_pos[1] - current_pos[1])
            next_state = (next_pos, next_direction)
            
            # Skip if already processed
            if next_state in closed_set:
                continue
            
            # Calculate tentative g_score
            tentative_g_score = g_scores[current_state] + weight
            
            # Check if new path is better
            if next_state not in g_scores or tentative_g_score < g_scores[next_state]:
                # Update path information
                g_scores[next_state] = tentative_g_score
                
                # Compute heuristic (cached)
                h_score = get_heuristic(next_pos, target_pos, heuristic_cache)
                
                # Update f_score
                f_score = tentative_g_score + h_score
                f_scores[next_state] = f_score
                
                # Update haunted steps for this path
                haunted_steps[next_state] = current_haunted_steps + 1
                
                # Construct new path
                new_path = path + [next_pos]
                
                # Increase counter for tie-breaking
                counter += 1
                
                # Add to open set
                heapq.heappush(open_set, (f_score, tentative_g_score, counter, next_state, new_path))
    
    # No path found
    return None, None, None

def get_heuristic(pos, target, cache=None):
    """
    Optimized and more informative heuristic function.
    Uses caching to avoid redundant calculations.
    
    Args:
        pos: Current position
        target: Target position
        cache: Optional dictionary for caching results
    
    Returns:
        Heuristic value (estimated cost to target)
    """
    # Use cache if provided
    if cache is not None:
        key = (pos, target)
        if key in cache:
            return cache[key]
    
    # Base Manhattan distance
    distance = abs(pos[0] - target[0]) + abs(pos[1] - target[1])
    
    # Scale by minimum movement cost for admissibility
    h_value = distance * STRAIGHT
    
    # Store in cache if provided
    if cache is not None:
        cache[(pos, target)] = h_value
    
    return h_value