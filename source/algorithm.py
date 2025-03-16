from specification import *
import heapq

def UCS_ghost(graph, start_pos, target_pos):
    """UCS algorithm for finding optimal path from ghost to player
    
    Uses priority queue to explore nodes in order of increasing cost.
    Considers haunted points effect on movement costs.
    """
    # Make a copy of haunted points to prevent affecting other algorithms
    original_haunted_points = set(graph.haunted_points)
    
    # Initialize priority queue with all possible starting directions
    frontier = []
    for direction in DIRECTIONS:
        heapq.heappush(frontier, (0, start_pos, direction, [start_pos]))
    
    # Keep track of visited states and costs
    visited = set()
    cost_so_far = {(start_pos, direction): 0 for direction in DIRECTIONS}
    haunted_steps = {(start_pos, direction): 0 for direction in DIRECTIONS}
    
    while frontier:
        # Get state with lowest cost from priority queue
        total_cost, current_pos, prev_direction, path = heapq.heappop(frontier)
        
        # Goal test - return path, cost, and next step
        if current_pos == target_pos:
            final_cost = calculate_path_cost(path, original_haunted_points)
            next_pos = path[1] if len(path) > 1 else start_pos
            return path, final_cost, next_pos
            
        # Skip if already visited
        state = (current_pos, prev_direction)
        if state in visited:
            continue
            
        visited.add(state)
        
        # Check if current position is a haunted point
        current_haunted_steps = haunted_steps[state]
        if current_pos in original_haunted_points:
            # Reset counter when on a haunted point
            current_haunted_steps = 0
        
        # Apply haunted point effect to movement costs
        neighbors = {}
        raw_neighbors = graph.graph.get((current_pos, prev_direction), {})
        
        for next_pos, base_weight in raw_neighbors.items():
            # If within haunted effect, all movements cost STRAIGHT
            weight = STRAIGHT if current_haunted_steps < HAUNTED_POINT_INDEX else base_weight
            neighbors[next_pos] = weight
        
        # Explore neighbors
        for next_pos, weight in neighbors.items():
            # Calculate direction to next position
            next_direction = (next_pos[0] - current_pos[0], next_pos[1] - current_pos[1])
            next_state = (next_pos, next_direction)
            new_cost = total_cost + weight
            
            # Update if found better path
            if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
                cost_so_far[next_state] = new_cost
                new_path = path + [next_pos]
                haunted_steps[next_state] = current_haunted_steps + 1
                heapq.heappush(frontier, (new_cost, next_pos, next_direction, new_path))
    
    # No path found
    return None, None, None


def BFS_ghost(graph, start_pos, target_pos):
    """BFS algorithm for finding shortest path from ghost to player
    
    Explores all nodes at present depth before moving to next depth.
    Guarantees shortest path in terms of number of steps.
    """
    # Initialize queue with all possible starting directions
    queue = []
    for direction in DIRECTIONS:
        queue.append((start_pos, direction, [start_pos]))
    
    visited = set()

    while queue:
        # Get first state from queue (FIFO)
        current_pos, current_dir, path = queue.pop(0)
        
        # Goal test
        if current_pos == target_pos:
            total_cost = calculate_path_cost(path, graph.haunted_points)
            next_pos = path[1] if len(path) > 1 else start_pos
            return path, total_cost, next_pos
        
        # Skip if already visited
        state = (current_pos, current_dir)
        if state in visited:
            continue
            
        visited.add(state)
        
        # Get all valid neighbors
        neighbors = get_valid_neighbors(graph, current_pos, current_dir)
        
        # Add unvisited neighbors to queue
        for next_pos, next_dir in neighbors:
            next_state = (next_pos, next_dir)
            
            if next_state not in visited:
                new_path = path + [next_pos]
                queue.append((next_pos, next_dir, new_path))

    # No path found
    return None, None, None


def get_valid_neighbors(graph, pos, direction):
    """Get valid neighbor positions and their directions
    
    Returns list of (position, direction) tuples that can be reached from current state.
    """
    neighbors = []
    # Get all neighbors from graph
    neighbor_dict = graph.get_neighbors_with_weights((pos, direction))
    
    # Calculate direction for each neighbor
    for next_pos in neighbor_dict:
        next_dir = (next_pos[0] - pos[0], next_pos[1] - pos[1])
        neighbors.append((next_pos, next_dir))
    
    return neighbors


def calculate_path_cost(path, haunted_points):
    """Calculate the total cost of a path, considering turns and haunted points
    
    Movement costs:
    - Straight movement: STRAIGHT (1 unit)
    - 90° turn: TURN (7 units)
    - 180° turn: BACK (14 units)
    - After haunted point: All movements cost STRAIGHT for 10 steps
    """
    if len(path) <= 1:
        return 0
    
    total_cost = 0
    remaining_haunted_steps = 0
    prev_dir = None
    
    for i in range(1, len(path)):
        prev_pos = path[i-1]
        curr_pos = path[i]
        # Calculate direction of current step
        curr_dir = (curr_pos[0] - prev_pos[0], curr_pos[1] - prev_pos[1])
        
        # Check if previous position was a haunted point
        if prev_pos in haunted_points:
            remaining_haunted_steps = HAUNTED_POINT_INDEX  # Reset to 10 steps
        
        # Determine movement cost
        if remaining_haunted_steps > 0:
            # Under haunted effect - all movements cost STRAIGHT
            cost = STRAIGHT
            remaining_haunted_steps -= 1
        else:
            # Normal movement costs based on direction change
            if prev_dir is None:
                # First movement
                cost = STRAIGHT
            else:
                if prev_dir == curr_dir:
                    # Continuing in same direction
                    cost = STRAIGHT
                elif (prev_dir[0] == -curr_dir[0] and prev_dir[1] == -curr_dir[1]):
                    # 180° turn (opposite direction)
                    cost = BACK
                else:
                    # 90° turn
                    cost = TURN
        
        prev_dir = curr_dir
        total_cost += cost
    
    return total_cost


def DFS_ghost(graph, start_pos, target_pos):
    """DFS algorithm for finding path from ghost to player
    
    Explores as far as possible along each branch before backtracking.
    Creates more unpredictable paths, not guaranteed to be optimal.
    """
    # Reset haunted steps counter
    graph.moves_since_haunted = 0
    
    # Initialize stack with all possible starting directions
    stack = []
    for direction in DIRECTIONS:
        stack.append((start_pos, direction, [start_pos]))
    
    visited = set()

    while stack:
        # Get last state from stack (LIFO)
        current_pos, current_dir, path = stack.pop()
        
        # Goal test
        if current_pos == target_pos:
            total_cost = calculate_path_cost(path, graph.haunted_points)
            next_pos = path[1] if len(path) > 1 else start_pos
            return path, total_cost, next_pos
        
        # Skip if already visited
        state = (current_pos, current_dir)
        if state in visited:
            continue
            
        visited.add(state)
        
        # Get all valid neighbors
        neighbors = get_valid_neighbors(graph, current_pos, current_dir)
        
        # Add unvisited neighbors to stack (will be explored in reverse order)
        for next_pos, next_dir in neighbors:
            next_state = (next_pos, next_dir)
            
            if next_state not in visited:
                new_path = path + [next_pos]
                stack.append((next_pos, next_dir, new_path))

    # No path found
    return None, None, None


def manhattan_distance(pos1, pos2):
    """Calculate Manhattan distance between two points
    
    Used as heuristic in A* algorithm.
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def A_star_ghost(graph, start_pos, target_pos):
    """A* algorithm for finding optimal path from ghost to player
    
    Combines UCS with heuristic to guide search towards target.
    Uses f(n) = g(n) + h(n) where:
    - g(n) is cost from start to current node
    - h(n) is estimated cost from current node to goal
    """
    # Make a copy of haunted points to prevent affecting other algorithms
    original_haunted_points = set(graph.haunted_points)
    heuristic_cache = {}  # Cache for faster heuristic calculations
    haunted_steps = {}    # Track haunted effect for each state independently
    
    # Initialize data structures
    open_set = []   # Priority queue of states to explore
    g_scores = {}   # Actual cost from start to each state
    f_scores = {}   # Total estimated cost (g + h) for each state
    
    # Initialize with all possible starting directions
    for direction in DIRECTIONS:
        state = (start_pos, direction)
        g_scores[state] = 0
        f_scores[state] = get_heuristic(start_pos, target_pos, heuristic_cache)
        haunted_steps[state] = 0
        # Add to open set: (f_score, g_score, unique_id, state, path)
        heapq.heappush(open_set, (f_scores[state], 0, id(state), state, [start_pos]))
    
    closed_set = set()  # States already evaluated
    counter = 0         # For tie-breaking when f_scores are equal
    
    while open_set:
        # Get state with lowest f_score
        _, _, _, current_state, path = heapq.heappop(open_set)
        current_pos, current_direction = current_state
        
        # Goal test
        if current_pos == target_pos:
            total_cost = calculate_path_cost(path, original_haunted_points)
            next_pos = path[1] if len(path) > 1 else current_pos
            return path, total_cost, next_pos
        
        # Skip if already evaluated
        if current_state in closed_set:
            continue
        
        # Mark as evaluated
        closed_set.add(current_state)
        
        # Check for haunted point effect
        current_haunted_steps = haunted_steps[current_state]
        if current_pos in original_haunted_points:
            # Reset counter when on a haunted point
            current_haunted_steps = 0
        
        # Apply haunted point effect to movement costs
        neighbors = {}
        raw_neighbors = graph.graph.get(current_state, {})
        
        for next_pos, base_weight in raw_neighbors.items():
            # If within haunted effect, all movements cost STRAIGHT
            weight = STRAIGHT if current_haunted_steps < HAUNTED_POINT_INDEX else base_weight
            neighbors[next_pos] = weight
        
        # Explore neighbors
        for next_pos, weight in neighbors.items():
            # Calculate direction to next position
            next_direction = (next_pos[0] - current_pos[0], next_pos[1] - current_pos[1])
            next_state = (next_pos, next_direction)
            
            # Skip if already evaluated
            if next_state in closed_set:
                continue
            
            # Calculate tentative g_score
            tentative_g_score = g_scores[current_state] + weight
            
            # Update if found better path
            if next_state not in g_scores or tentative_g_score < g_scores[next_state]:
                # Update path information
                g_scores[next_state] = tentative_g_score
                
                # Calculate heuristic (from cache if available)
                h_score = get_heuristic(next_pos, target_pos, heuristic_cache)
                
                # Calculate f_score = g_score + h_score
                f_score = tentative_g_score + h_score
                f_scores[next_state] = f_score
                
                # Update haunted steps counter
                haunted_steps[next_state] = current_haunted_steps + 1
                
                # Create new path
                new_path = path + [next_pos]
                
                # Increment counter for tie-breaking
                counter += 1
                
                # Add to open set with updated values
                heapq.heappush(open_set, (f_score, tentative_g_score, counter, next_state, new_path))
    
    # No path found
    return None, None, None


def get_heuristic(pos, target, cache=None):
    """Calculate heuristic with caching for better performance
    
    Uses Manhattan distance scaled by STRAIGHT cost for admissibility.
    Caching improves performance by avoiding redundant calculations.
    """
    # Check cache first
    if cache is not None:
        key = (pos, target)
        if key in cache:
            return cache[key]
    
    # Calculate Manhattan distance
    distance = abs(pos[0] - target[0]) + abs(pos[1] - target[1])
    
    # Scale by minimum movement cost to ensure admissibility
    h_value = distance * STRAIGHT
    
    # Store in cache
    if cache is not None:
        cache[(pos, target)] = h_value
    
    return h_value