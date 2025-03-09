import pygame
from pathlib import Path

# Game constants
WALL = '#'
PLAYER = 'P'
EMPTY = ' '
POINT = '.'

# Ghost identifiers
BLUE_GHOST = 'B'
PINK_GHOST = 'N'
ORANGE_GHOST = 'O'
RED_GHOST = 'R'
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
STRAIGHT = 2
TURN = 5
BACK = 10

# Map direction
MAP_DIR = str(Path(__file__).parent.parent / "map" / "map.txt")