import sys
import argparse
from game_play import game_text
from test import test_interface
from map_implement import view_graph_interactive
from pacman import PacmanGame2D

def run_pacman_2d():
    """Run the 2D Pacman game"""
    game = PacmanGame2D()
    game.run()

def main():
    """Main function to parse command line arguments and run the appropriate function"""
    parser = argparse.ArgumentParser(description='AI Project - Pacman Game')
    
    # Create mutually exclusive group for the main command
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-text', action='store_true', help='Run text-based game')
    group.add_argument('-2d', dest='twod', action='store_true', help='Run 2D game')
    group.add_argument('-graph', action='store_true', help='Run interactive graph visualization')
    group.add_argument('-algo', action='store_true', help='Test algorithms')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the appropriate function based on arguments
    if args.text:
        game_text()
    elif args.graph:
        view_graph_interactive()
    elif args.algo:
        test_interface()
    elif args.twod:
        run_pacman_2d()

if __name__ == "__main__":
    main()