import pygame
from pathlib import Path

# Game constants
WALL = '#'
PLAYER = 'P'
EMPTY = ' '
POINT = '.'

# Ghost identifiers
BLUE_GHOST = 'B'   # Uses BFS algorithm
PINK_GHOST = 'N'   # Uses A* algorithm
ORANGE_GHOST = 'O' # Uses DFS algorithm
RED_GHOST = 'R'    # Uses UCS algorithm
HAUNTED_POINT = 'H'

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
PINK = (255, 192, 203)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Weight
STRAIGHT = 1
TURN = 7
BACK = 14

# Game index
HAUNTED_POINT_INDEX = 10
SPEED = 100
PLAYER_MOVEMENT = 0.2# 0.4 seconds between moves

# Movement types for graph weights
STRAIGHT_MOVEMENT = 0
TURN_MOVEMENT = 1
BACK_MOVEMENT = 2

# Định nghĩa các hằng số cho FPS
TARGET_FPS = 300 
FRAME_TIME = 1.0 / TARGET_FPS
GHOST_UPDATE_INTERVAL = 0.5
BASE_GHOST_UPDATE_INTERVAL = 0.25

# Map direction
MAP_DIR = str(Path(__file__).parent.parent / "map" / "map.txt")