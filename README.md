# Pacman AI Project

A Python implementation of Pacman game with AI ghost behaviors using different pathfinding algorithms.

## Project Structure
```
project1/
├── source/
│   ├── algorithm.py     # Pathfinding algorithms implementation
│   ├── map_implement.py # Map graph and movement logic
│   ├── game_map.py     # Map loading and representation
│   └── test.py         # Testing and visualization
└── map/
    └── map.txt         # Game map file
```

## Features

- Multiple pathfinding algorithms:
  - Uniform Cost Search (UCS)
  - Breadth-First Search (BFS)
  - Depth-First Search (DFS)
  - A* Search

- Ghost behaviors:
  - Different ghosts use different pathfinding strategies
  - Special haunted points that modify ghost movement
  - Dynamic path weights based on movement direction

## Requirements

- Python 3.x
- Pygame 2.6.1
- SDL 2.28.4

## Installation

1. Clone the repository:
```bash
git clone https://github.com/dtduy23/Pacman.git
cd project1
```

2. Install required packages:
```bash
pip install pygame
```

## Usage

Run the main test file:
```bash
python source/test.py
```

## Game Elements

- `P`: Pacman (player)
- `B`: Blue ghost
- `R`: Red ghost
- `O`: Orange ghost
- `N`: Pink ghost
- `H`: Haunted point
- `#`: Wall
- `.`: Normal point
- ` `: Empty space

## Algorithm Details

### UCS (Uniform Cost Search)
- Uses priority queue based on movement cost
- Considers turn penalties in path calculation
- Optimal for finding least-cost path

### A* Search
- Uses Manhattan distance heuristic
- Balances path cost with distance to target
- Efficient for finding optimal paths

### Movement Costs
- Straight movement: 2 units
- 90° turn: 5 units
- 180° turn: 10 units
- All movements cost 2 units for 20 moves after hitting a haunted point