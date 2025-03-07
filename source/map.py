from specification import *

class Map:
    def __init__(self, layout):
        self.layout = layout
        self.height = len(layout)
        self.width = len(layout[0])
        self.player_pos = self.find_position(PLAYER)
        self.ghost_positions = {
            'blue': self.find_position(BLUE_GHOST),
            'pink': self.find_position(PINK_GHOST),
            'red': self.find_position(RED_GHOST),
            'orange': self.find_position(ORANGE_GHOST)
        }
        self.haunted_points = self.find_all_positions(HAUNTED_POINT)
        self.dots = self.count_dots()

    def find_position(self, char):
        for y in range(self.height):
            for x in range(self.width):
                if self.layout[y][x] == char:
                    return (x, y)
        return None

    def find_all_positions(self, char):
        positions = []
        for y in range(self.height):
            for x in range(self.width):
                if self.layout[y][x] == char:
                    positions.append((x, y))
        return positions

    def count_dots(self):
        count = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.layout[y][x] == '.': 
                    count += 1
        return count

    @staticmethod
    def load_map(filename):
        try:
            with open(filename, 'r') as f:
                layout = [list(line.strip()) for line in f]
            return Map(layout)
        except FileNotFoundError:
            print(f"Error: Map file {filename} not found")
            return None

# # Test code
# if __name__ == "__main__":
#     game_map = Map.load_map(r"D:\Năm 2\Kỳ 2\csAI\project1\map\maze.txt")

#     if game_map:
#         # Print map layout
#         print("\nMap Layout:")
#         for row in game_map.layout:
#             print(''.join(row))
            
#         print("\nMap Information:")
#         print(f"Dimensions: {game_map.width}x{game_map.height}")
#         print(f"Pacman position: {game_map.player_pos}")
#         print("\nGhost positions:")
#         for ghost, pos in game_map.ghost_positions.items():
#             print(f"- {ghost.capitalize()} ghost: {pos}")
#         print(f"\nHaunted points: {game_map.haunted_points}")
#         print(f"Number of dots: {game_map.dots}")