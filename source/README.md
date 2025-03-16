# Pacman AI Project

A Python implementation of the classic Pacman game with AI ghost behaviors using different pathfinding algorithms.

## Project Structure
```
project1/
├── source/
│   ├── algorithm.py     # Pathfinding algorithms implementation
│   ├── game_map.py      # Map loading and representation
│   ├── game_play.py     # Text-based game implementation
│   ├── main.py          # Command-line interface for the game
│   ├── map_implement.py # Map graph and movement logic
│   ├── pacman.py        # 2D game implementation with Pygame
│   ├── specification.py # Game constants and parameters
│   └── test.py          # Algorithm testing and visualization
├── map/
│   └── map.txt          # Game map file
└── assets/              # Game graphics and sounds (for 2D version)
```

## Features

- Multiple pathfinding algorithms:
  - Uniform Cost Search (UCS)
  - Breadth-First Search (BFS)
  - Depth-First Search (DFS)
  - A* Search

- Ghost behaviors:
  - Each ghost uses a different pathfinding algorithm
  - Special haunted points that modify ghost movement
  - Dynamic path weights based on movement direction

- Two game modes:
  - Text-based console version
  - 2D graphical version with Pygame

## Requirements

- Python 3.x
- Pygame 2.6.1+ (for 2D version)

## Installation

1. Clone the repository:
```bash
git https://github.com/dtduy23/Pacman.git
cd project1
```

2. Install required packages:
```bash
pip install pygame
```

## Usage

The game offers multiple ways to run it through command-line arguments:

```bash
# Run the text-based version
python source/main.py -text

# Run the 2D version with Pygame
python source/main.py -2d

# View the interactive graph representation
python source/main.py -graph

# Test and visualize the pathfinding algorithms
python source/main.py -algo
```

## Game Elements

- `P`: Pacman (player)
- `B`: Blue ghost (uses BFS algorithm)
- `R`: Red ghost (uses UCS algorithm)
- `O`: Orange ghost (uses DFS algorithm)
- `N`: Pink ghost (uses A* algorithm)
- `H`: Haunted point
- `#`: Wall
- `.`: Normal point (collect all to win)
- ` `: Empty space

## Game Rules

1. Move Pacman through the maze using arrow keys or WASD
2. Collect all normal points (`.`) to win the game
3. Avoid the ghosts - if they catch you, the game is over
4. Haunted points (`H`) have special effects:
   - When Pacman collects a haunted point, he earns 10 points
   - When a ghost passes over a haunted point, its movement speed is fixed at the STRAIGHT speed for the next 10 steps

## Algorithm Details

### UCS (Uniform Cost Search) - Red Ghost
- Uses priority queue based on movement cost
- Considers movement penalties depending on direction changes
- Optimal for finding least-cost path

### BFS (Breadth-First Search) - Blue Ghost
- Explores all nodes at present depth before moving to nodes at next depth
- Equal weight for all movements (without haunted effect)
- Optimal for unweighted graphs

### DFS (Depth-First Search) - Orange Ghost
- Explores as far as possible along each branch before backtracking
- Creates more erratic and unpredictable paths
- May not find the shortest path

### A* Search - Pink Ghost
- Uses Manhattan distance heuristic
- Balances path cost with distance to target
- Efficient for finding optimal paths while exploring fewer nodes than UCS

### Movement Costs
- Straight movement: 1 units
- 90° turn: 7 units
- 180° turn: 14 units
- When a ghost passes over a haunted point (`H`), all movements cost 2 units for the next 10 steps

## Controls

### Text-based version:
- `W` or `↑`: Move up
- `S` or `↓`: Move down
- `A` or `←`: Move left
- `D` or `→`: Move right
- `Q`: Quit the game

### 2D version:
- `W` or `↑`: Move up
- `S` or `↓`: Move down
- `A` or `←`: Move left
- `D` or `→`: Move right
- `ESC`: Quit the game
- `SPACE`: Restart after game over

## Acknowledgements

This project was developed as part of an AI course to demonstrate various graph search algorithms in a practical application.

## License

MIT License