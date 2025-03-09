from specification import *
from collections import defaultdict

"""
MapGraph class for creating a weighted graph from the game map
"""

# class MapGraph:
#     def __init__(self, game_map):
#         self.map = game_map
#         self.graph = self._create_weighted_graph()
#         self.positions = self._get_positions_dict()

#     def _calculate_turn_weight(self, current_direction, new_direction):
#         """Calculate weight based on turning angle
#         Returns:
#             2 for straight (0 degrees)
#             5 for 90 degree turn
#             10 for 180 degree turn
#         """
#         if current_direction == new_direction: # Straight
#             return STRAIGHT
        
#         # Calculate angle between current and new direction
#         dx1, dy1 = current_direction
#         dx2, dy2 = new_direction
        
#         # Check if directions are opposite
#         if (dx1, dy1) == (-dx2, -dy2):
#             return BACK
        
#         # Otherwise, it's a 90 degree turn
#         return TURN
    
#     def _create_weighted_graph(self):
#         # Create adjacency list with weights
#         graph = defaultdict(dict)
        
#         for y in range(self.map.height):
#             for x in range(self.map.width):
#                 if self.map.layout[y][x] == WALL:
#                     continue
                
#                 current_pos = (x, y)
                
#                 # For each position, consider all possible previous directions
#                 for prev_dx, prev_dy in DIRECTIONS:
#                     prev_direction = (prev_dx, prev_dy)
                    
#                     # Check each possible new direction
#                     for new_dx, new_dy in DIRECTIONS:
#                         new_x, new_y = x + new_dx, y + new_dy
#                         new_direction = (new_dx, new_dy)
                        
#                         if (0 <= new_x < self.map.width and 
#                             0 <= new_y < self.map.height and 
#                             self.map.layout[new_y][new_x] != WALL):
                            
#                             # Calculate weight based on turn
#                             weight = self._calculate_turn_weight(prev_direction, new_direction)
                            
#                             # Store in graph with direction information
#                             if (current_pos, prev_direction) not in graph:
#                                 graph[(current_pos, prev_direction)] = {}
                            
#                             graph[(current_pos, prev_direction)][(new_x, new_y)] = weight
        
#         return graph

#     def _get_positions_dict(self):
#         """Returns a dictionary mapping position types to their coordinates"""
#         positions = {
#             'player': self.map.player_pos,
#             'ghosts': self.map.ghost_positions,
#             'haunted_points': self.map.haunted_points
#         }
#         return positions

#     def get_neighbors(self, pos):
#         """Get all valid neighbors for a given position"""
#         return self.graph[pos]

#     def is_valid_move(self, from_pos, to_pos):
#         """Check if moving from one position to another is valid"""
#         return to_pos in self.graph[from_pos]

#     def get_path_options(self, current_pos):
#         """Get all possible paths from current position"""
#         return self.graph[current_pos]
#     def get_neighbors_with_weights(self, state):
#         """
#         Get all valid neighbors and their weights from current position and direction
#         Args:
#             state: Tuple of (position, direction) where:
#                   position is (x,y)
#                   direction is (dx,dy)
#         Returns:
#             Dictionary of {next_position: weight}
#         """
#         current_pos, coming_from = state
#         return self.graph.get((current_pos, coming_from), {})


"""
MapGraph class for creating a weighted graph from the game map
"""

class MapGraph:
    def __init__(self, game_map):
        self.map = game_map
        self.graph = self._create_weighted_graph()
        self.positions = self._get_positions_dict()
        self.haunted_points = set(self.map.haunted_points)
        self.moves_since_haunted = 0
        self.max_moves = 20  # Maximum moves before slowing down

    def _calculate_turn_weight(self, current_direction, new_direction):
        """Calculate weight based on turning angle
        Returns:
            2 for straight (0 degrees)
            5 for 90 degree turn
            10 for 180 degree turn
        """
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
        
        # Create a copy of neighbors with potentially modified weights
        modified_neighbors = {}
        
        for next_pos, weight in neighbors.items():
            # If the ghost is at a haunted point, all movement costs are 2
            if current_pos in self.haunted_points:
                modified_neighbors[next_pos] = STRAIGHT  # Always use STRAIGHT (2) at haunted points
                self.moves_since_haunted = 0  # Reset counter when at haunted point
            else:
                # If it's been too long since visiting a haunted point, increase weights
                if self.moves_since_haunted >= self.max_moves:
                    # Double the weight to simulate slowing down
                    modified_neighbors[next_pos] = weight * 2
                else:
                    modified_neighbors[next_pos] = weight
                    
        # Increment the move counter if not at a haunted point
        if current_pos not in self.haunted_points:
            self.moves_since_haunted += 1
                
        return modified_neighbors
    
    def update_haunted_status(self, current_pos):
        """
        Update the ghost's status when it moves to a new position
        Args:
            current_pos: The current position of the ghost (x,y)
        """
        # If ghost is at a haunted point, reset the move counter
        if current_pos in self.haunted_points:
            self.moves_since_haunted = 0
        else:
            # Increment the move counter if not at a haunted point
            self.moves_since_haunted += 1

# # Test code
# if __name__ == "__main__":
#     # Load the map
#     game_map = Map.load_map(r"D:\Năm 2\Kỳ 2\csAI\project1\map\maze.txt")
#     map_graph = MapGraph(game_map)
    
#     # Print all adjacency lists
#     print("\nComplete Adjacency List:")
#     print("------------------------")
#     for (pos, direction), neighbors in sorted(map_graph.graph.items()):
#         print(f"\nNode at position {pos} coming from direction {direction}:")
#         for next_pos, weight in neighbors.items():
#             print(f"  -> To {next_pos} with weight {weight}")
    
#     # Print summary statistics
#     print("\nGraph Statistics:")
#     print(f"Total nodes (position-direction pairs): {len(map_graph.graph)}")
#     total_edges = sum(len(neighbors) for neighbors in map_graph.graph.values())
#     print(f"Total edges: {total_edges}")
    
#     # Print Pacman's position and its neighbors
#     pacman_pos = map_graph.positions['player']
#     print(f"\nPacman position: {pacman_pos}")
#     for direction in DIRECTIONS:
#         print(f"\nPacman's moves coming from direction {direction}:")
#         neighbors = map_graph.graph.get((pacman_pos, direction), {})
#         for next_pos, weight in neighbors.items():
#             print(f"  -> Can move to {next_pos} with weight {weight}")
