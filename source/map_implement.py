from specification import *
from collections import defaultdict

"""
MapGraph class for creating a weighted graph from the game map
"""


class MapGraph:
    def __init__(self, game_map):
        self.map = game_map
        self.haunted_points = set(self.map.haunted_points.copy())  # Create a separate set for tracking
        self.moves_since_haunted = 0
        self.max_moves = HAUNTED_POINT_INDEX  # Default max moves before penalty
        self.graph = self._create_weighted_graph()
        self.positions = self._get_positions_dict()

    def _calculate_turn_weight(self, current_direction, new_direction):
        if current_direction == new_direction: # Straight
            return STRAIGHT
        
        # Calculate angle between current and new direction
        dx1, dy1 = current_direction
        dx2, dy2 = new_direction
        
        # Check if directions are opposite
        if (dx1, dy1) == (-dx2, -dy2):
            return BACK
        
        # Otherwise, it's a 90 degree turn
        return TURN
    
    def _create_weighted_graph(self):
        # Create adjacency list with weights
        graph = defaultdict(dict)
        
        for y in range(self.map.height):
            for x in range(self.map.width):
                if self.map.layout[y][x] == WALL:
                    continue
                
                current_pos = (x, y)
                
                # For each position, consider all possible previous directions
                for prev_dx, prev_dy in DIRECTIONS:
                    prev_direction = (prev_dx, prev_dy)
                    
                    # Check each possible new direction
                    for new_dx, new_dy in DIRECTIONS:
                        new_x, new_y = x + new_dx, y + new_dy
                        new_direction = (new_dx, new_dy)
                        
                        if (0 <= new_x < self.map.width and 
                            0 <= new_y < self.map.height and 
                            self.map.layout[new_y][new_x] != WALL):
                            
                            # Calculate weight based on turn
                            weight = self._calculate_turn_weight(prev_direction, new_direction)
                            
                            # Store in graph with direction information
                            if (current_pos, prev_direction) not in graph:
                                graph[(current_pos, prev_direction)] = {}
                            
                            graph[(current_pos, prev_direction)][(new_x, new_y)] = weight
        
        return graph

    def _get_positions_dict(self):
        """Returns a dictionary mapping position types to their coordinates"""
        positions = {
            'player': self.map.player_pos,
            'ghosts': self.map.ghost_positions,
            'haunted_points': self.map.haunted_points
        }
        return positions

    def get_neighbors(self, pos):
        """Get all valid neighbors for a given position"""
        return self.graph[pos]

    def is_valid_move(self, from_pos, to_pos):
        """Check if moving from one position to another is valid"""
        return to_pos in self.graph[from_pos]

    def get_path_options(self, current_pos):
        """Get all possible paths from current position"""
        return self.graph[current_pos]
        
    def get_neighbors_with_weights(self, state):
        """
        Get all valid neighbors and their weights from current position and direction
        Args:
            state: Tuple of (position, direction) where:
                  position is (x,y)
                  direction is (dx,dy)
        Returns:
            Dictionary of {next_position: weight}
        """
        current_pos, coming_from = state
        neighbors = self.graph.get((current_pos, coming_from), {})
        modified_neighbors = {}
        
        # Check if this position is a haunted point
        if current_pos in self.haunted_points:
            # Reset counter when on a haunted point
            self.moves_since_haunted = 0
        
        # Apply weights based on counter
        if self.moves_since_haunted < self.max_moves:
            # In 20 steps after haunted point - all movements cost 2
            for next_pos, _ in neighbors.items():
                modified_neighbors[next_pos] = STRAIGHT  # STRAIGHT = 2
        else:
            # Normal mode - use original weights
            for next_pos, weight in neighbors.items():
                modified_neighbors[next_pos] = weight
        
        # Increment counter here (always increment after checking)
        self.moves_since_haunted += 1
        
        return modified_neighbors

    def update_haunted_status(self, current_pos):
        """
        Update the haunted status based on current position
        This is needed for algorithms that don't use get_neighbors_with_weights directly
        """
        if current_pos in self.haunted_points:
            # DON'T remove the haunted point, just reset counter
            # self.haunted_points.remove(current_pos)  # <-- REMOVED THIS LINE
            self.moves_since_haunted = 0  # Reset counter when visiting a haunted point
        else:
            # Increment the move counter if not at a haunted point
            self.moves_since_haunted += 1

    def _determine_movement_type(self, current_direction, new_direction):
        """Determine if moving from current to new direction is straight, turn, or back"""
        if current_direction == new_direction:
            return STRAIGHT_MOVEMENT
        
        # Calculate if directions are opposite (back movement)
        dx1, dy1 = current_direction
        dx2, dy2 = new_direction
        
        if (dx1, dy1) == (-dx2, -dy2):
            return BACK_MOVEMENT
        
        # Otherwise, it's a turn
        return TURN_MOVEMENT
    
    def add_temporary_obstacle(self, pos):
        """Add a temporary obstacle at the specified position"""
        if not hasattr(self, 'temporary_obstacles'):
            self.temporary_obstacles = set()
        
        self.temporary_obstacles.add(pos)
        
        # Update the graph to reflect the obstacle
        x, y = pos
        
        # Remove edges to/from this position
        for direction in DIRECTIONS:
            dx, dy = direction
            neighbor_pos = (x + dx, y + dy)
            
            # Remove edge from neighbor to pos
            if neighbor_pos in self.graph:
                for neighbor_dir in DIRECTIONS:
                    neighbor_state = (neighbor_pos, neighbor_dir)
                    if neighbor_state in self.graph and pos in self.graph[neighbor_state]:
                        del self.graph[neighbor_state][pos]
            
            # Remove edge from pos to neighbor
            pos_state = (pos, direction)
            if pos_state in self.graph and neighbor_pos in self.graph[pos_state]:
                del self.graph[pos_state][neighbor_pos]

    def remove_temporary_obstacle(self, pos):
        """Remove a temporary obstacle and rebuild the graph connections"""
        if not hasattr(self, 'temporary_obstacles') or pos not in self.temporary_obstacles:
            return
        
        self.temporary_obstacles.remove(pos)
        
        # Rebuild connections for this position
        x, y = pos
        
        # Check all four directions
        for direction in DIRECTIONS:
            dx, dy = direction
            neighbor_pos = (x + dx, y + dy)
            
            # Skip if out of bounds
            if not (0 <= neighbor_pos[0] < self.map.width and 0 <= neighbor_pos[1] < self.map.height):
                continue
            
            # Skip if it's a wall
            if self.map.layout[neighbor_pos[1]][neighbor_pos[0]] == '#':
                continue
            
            # Skip if it's still a temporary obstacle
            if hasattr(self, 'temporary_obstacles') and neighbor_pos in self.temporary_obstacles:
                continue
                
            # Determine the cost based on the turn type
            # Straight, Turn, Back based on current direction
            for pos_dir in DIRECTIONS:
                pos_state = (pos, pos_dir)
                
                # Determine if it's a straight, turn, or back movement
                movement_type = self._determine_movement_type(pos_dir, (dx, dy))
                if movement_type == STRAIGHT_MOVEMENT:
                    cost = STRAIGHT
                elif movement_type == TURN_MOVEMENT:
                    cost = TURN
                else:  # BACK_MOVEMENT
                    cost = BACK
                    
                # Add the edge to the graph
                if pos_state not in self.graph:
                    self.graph[pos_state] = {}
                self.graph[pos_state][neighbor_pos] = cost

    def remove_all_temporary_obstacles(self):
        """Remove all temporary obstacles and rebuild the graph connections"""
        if not hasattr(self, 'temporary_obstacles'):
            return
            
        obstacles = list(self.temporary_obstacles)  # Make a copy to avoid modification during iteration
        for pos in obstacles:
            self.remove_temporary_obstacle(pos)
    
from specification import *
from game_map import Map
from map_implement import MapGraph

def direction_to_name(direction):
    """Convert direction tuple to readable name"""
    if direction == UP:
        return "UP"
    elif direction == DOWN:
        return "DOWN"
    elif direction == LEFT:
        return "LEFT"
    elif direction == RIGHT:
        return "RIGHT"
    return "UNKNOWN"

def print_graph_sample(graph, sample_limit=5):
    """Print a sample of the graph structure"""
    count = 0
    print("\n=== GRAPH STRUCTURE SAMPLE ===")
    
    # Get a list of keys (states) for deterministic ordering
    states = list(graph.keys())
    states.sort()  # Sort for consistent output
    
    for state in states[:sample_limit]:
        pos, direction = state
        dir_name = direction_to_name(direction)
        
        print(f"\nState: Position {pos}, Coming from direction {dir_name}")
        print("-" * 50)
        
        # Get neighbors for this state
        neighbors = graph[state]
        
        if not neighbors:
            print("  No valid neighbors")
            continue
        
        print("  Neighbors:")
        print("  " + "-" * 45)
        print(f"  {'Next Position':<15} {'Direction':<10} {'Weight':<8} {'Turn Type'}")
        print("  " + "-" * 45)
        
        # Sort neighbors for consistent output
        neighbor_list = list(neighbors.items())
        neighbor_list.sort()
        
        for next_pos, weight in neighbor_list:
            # Calculate direction to this neighbor
            next_dir = (next_pos[0] - pos[0], next_pos[1] - pos[1])
            next_dir_name = direction_to_name(next_dir)
            
            # Determine turn type
            turn_type = "STRAIGHT"
            if direction == next_dir:
                turn_type = "STRAIGHT"
            elif (direction[0] == -next_dir[0] and direction[1] == -next_dir[1]):
                turn_type = "BACK"
            else:
                turn_type = "TURN"
            
            print(f"  {str(next_pos):<15} {next_dir_name:<10} {weight:<8} {turn_type}")
        
        count += 1
        
    print("\nTotal states in graph:", len(graph))
    
    # Count states per position
    positions_count = {}
    for pos, direction in graph.keys():
        if pos not in positions_count:
            positions_count[pos] = 0
        positions_count[pos] += 1
    
    # Count how many positions have all 4 directions
    positions_with_all_directions = sum(1 for count in positions_count.values() if count == 4)
    print(f"Positions with all 4 directions: {positions_with_all_directions}/{len(positions_count)}")
    
    # Count total edges
    total_edges = sum(len(neighbors) for neighbors in graph.values())
    print(f"Total edges in graph: {total_edges}")
    print(f"Average edges per state: {total_edges / len(graph):.2f}")

def analyze_state_transitions(graph, pos, coming_direction):
    """Analyze all possible transitions from a specific state"""
    state = (pos, coming_direction)
    dir_name = direction_to_name(coming_direction)
    
    print(f"\n=== TRANSITIONS FROM POSITION {pos} COMING FROM {dir_name} ===")
    
    if state not in graph:
        print("This state doesn't exist in the graph!")
        return
    
    neighbors = graph[state]
    if not neighbors:
        print("No valid neighbors from this state.")
        return
    
    print("-" * 60)
    print(f"{'Next Position':<15} {'Direction':<10} {'Weight':<8} {'Turn Type'}")
    print("-" * 60)
    
    # Sort neighbors for consistent output
    neighbor_list = list(neighbors.items())
    neighbor_list.sort()
    
    for next_pos, weight in neighbor_list:
        # Calculate direction to this neighbor
        next_dir = (next_pos[0] - pos[0], next_pos[1] - pos[1])
        next_dir_name = direction_to_name(next_dir)
        
        # Determine turn type
        if coming_direction == next_dir:
            turn_type = "STRAIGHT (weight 2)"
        elif (coming_direction[0] == -next_dir[0] and coming_direction[1] == -next_dir[1]):
            turn_type = "BACK (weight 10)"
        else:
            turn_type = "TURN (weight 5)" 
        
        print(f"{str(next_pos):<15} {next_dir_name:<10} {weight:<8} {turn_type}")

def examine_weights_around_position(graph, pos):
    """Examine weights for all directions around a position"""
    print(f"\n=== EXAMINING ALL DIRECTIONS AT POSITION {pos} ===")
    
    found = False
    for direction in [UP, DOWN, LEFT, RIGHT]:
        state = (pos, direction)
        if state in graph:
            found = True
            print(f"\nComing from direction: {direction_to_name(direction)}")
            analyze_state_transitions(graph, pos, direction)
    
    if not found:
        print("This position doesn't exist in the graph!")

def view_graph_interactive():
    """Interactive graph exploration functionality"""
    # Load the map
    map_obj = Map.load_map(MAP_DIR)
    if map_obj is None:
        print("Failed to load map!")
        return
    
    # Create the graph
    map_graph = MapGraph(map_obj)
    graph = map_graph.graph
    
    # Print basic info
    print("Map size:", map_obj.width, "x", map_obj.height)
    print("Player position:", map_obj.player_pos)
    print("Haunted points:", map_obj.haunted_points)
    
    # Print a sample of the graph structure
    print_graph_sample(graph)
    
    # Let the user examine specific positions
    while True:
        print("\n" + "=" * 60)
        print("Enter coordinates to examine state transitions (or q to quit):")
        user_input = input("Position (x,y): ")
        
        if user_input.lower() == 'q':
            break
        
        try:
            x, y = map(int, user_input.strip().replace('(', '').replace(')', '').split(','))
            examine_weights_around_position(graph, (x, y))
        except ValueError:
            print("Invalid input! Please enter coordinates as 'x,y'")
    
    print("Done!")

if __name__ == "__main__":
    view_graph_interactive()