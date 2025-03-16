import sys
import argparse
import os
from game_play import GamePlay
from game_map import Map
from map_implement import MapGraph
from specification import *
from algorithm import UCS_ghost, BFS_ghost, DFS_ghost, A_star_ghost
import pygame

def view_algorithm():
    """Display the algorithm's operation with visualization"""
    print("Viewing algorithm operation...")
    try:
        # Tải bản đồ
        game_map = Map.load_map(MAP_DIR)
        if not game_map:
            print("Error loading map!")
            return
        
        # Khởi tạo đồ thị
        graph = MapGraph(game_map)
        
        # Hiển thị bản đồ
        print("\nMap:")
        for row in game_map.layout:
            print(''.join(row))
        
        # Lấy vị trí người chơi và ma
        player_pos = game_map.player_pos
        ghost_positions = game_map.ghost_positions
        
        # Hiển thị các thuật toán
        print("\nAlgorithm Operation Demonstration:")
        print(f"Player position: {player_pos}")
        
        # Chạy từng thuật toán và hiển thị kết quả
        for ghost_type, ghost_pos in ghost_positions.items():
            print(f"\n{ghost_type} Ghost at {ghost_pos}")
            
            if ghost_type == BLUE_GHOST:
                path, cost, next_pos = BFS_ghost(graph, ghost_pos, player_pos)
                algorithm_name = "BFS"
            elif ghost_type == ORANGE_GHOST:
                path, cost, next_pos = DFS_ghost(graph, ghost_pos, player_pos)
                algorithm_name = "DFS"
            elif ghost_type == RED_GHOST:
                path, cost, next_pos = UCS_ghost(graph, ghost_pos, player_pos)
                algorithm_name = "UCS"
            elif ghost_type == PINK_GHOST:
                path, cost, next_pos = A_star_ghost(graph, ghost_pos, player_pos)
                algorithm_name = "A*"
            
            print(f"Using {algorithm_name} algorithm")
            if path:
                print(f"Path found: {path}")
                print(f"Path cost: {cost}")
                print(f"Next position: {next_pos}")
            else:
                print("No path found")
    
    except Exception as e:
        print(f"Error during algorithm visualization: {e}")

def play_game():
    """Allow the user to play the game"""
    print("Starting game...")
    try:
        # Kiểm tra xem có Pygame không
        if 'pygame' in sys.modules:
            # Nếu có Pygame, sử dụng giao diện 2D
            try:
                from pacman import PacmanGame2D
                game = PacmanGame2D()
                game.run()
            except Exception as e:
                print(f"Error starting 2D game: {e}")
                print("Falling back to text-based version...")
                text_game = GamePlay()
                text_game.play()
        else:
            # Nếu không có Pygame, sử dụng giao diện text-based
            text_game = GamePlay()
            text_game.play()
    except Exception as e:
        print(f"Error during game play: {e}")

def view_graph():
    """Display how the graph is represented"""
    print("Viewing graph representation...")
    try:
        # Tải bản đồ
        game_map = Map.load_map(MAP_DIR)
        if not game_map:
            print("Error loading map!")
            return
        
        # Khởi tạo đồ thị
        graph = MapGraph(game_map)
        
        # Hiển thị bản đồ
        print("\nMap:")
        for row in game_map.layout:
            print(''.join(row))
        
        # Hiển thị đồ thị
        print("\nGraph Representation:")
        for node, edges in graph.graph.items():
            print(f"{node}: {edges}")
    
    except Exception as e:
        print(f"Error during graph visualization: {e}")

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description='AI Project - Graph Algorithm Visualization')
    
    # Create mutually exclusive group (user can only select one option)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-a', '--algorithm', action='store_true', help='View algorithm operation')
    group.add_argument('-p', '--play', action='store_true', help='Play the game')
    group.add_argument('-g', '--graph', action='store_true', help='View graph representation')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute based on the chosen option
    if args.algorithm:
        view_algorithm()
    elif args.play:
        play_game()
    elif args.graph:
        view_graph()

if __name__ == "__main__":
    main()