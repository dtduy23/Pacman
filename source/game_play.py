import os
import keyboard
import time
import colorama
from colorama import Fore, Back, Style
from specification import *
from game_map import Map
from map_implement import MapGraph
from algorithm import UCS_ghost, BFS_ghost, DFS_ghost, A_star_ghost
import threading
import random

# Initialize colorama
colorama.init(autoreset=True)



class GamePlay:
    def __init__(self, map_dir=MAP_DIR):
        """Initialize game with a map"""
        self.game_map = Map.load_map(map_dir)
        if not self.game_map:
            print("Error loading map!")
            exit(1)
            
        self.graph = MapGraph(self.game_map)
        self.player_pos = self.game_map.player_pos
        self.planned_next_positions = {}
        self.planned_positions_lock = threading.Lock()

        # Create a copy of the map layout that we'll modify
        self.map_display = [list(row) for row in self.game_map.layout]
        
        # Initialize ghost positions and assign letters based on algorithm name
        self.ghosts = {}
        self.initial_ghost_positions = set()

        for ghost_type, pos in self.game_map.ghost_positions.items():
            # Get the first letter of the algorithm name
            if ghost_type == BLUE_GHOST:
                letter = 'B'  # Blue ghost uses BFS
                color = Back.CYAN
            elif ghost_type == ORANGE_GHOST:
                letter = 'O'  # Orange ghost uses DFS
                color = Back.YELLOW
            elif ghost_type == RED_GHOST:
                letter = 'R'  # Red ghost uses UCS
                color = Back.RED
            elif ghost_type == PINK_GHOST:
                letter = 'N'  # Pink ghost uses A*
                color = Back.MAGENTA
                
            self.ghosts[ghost_type] = {
                'pos': pos,
                'previous_direction': UP,  # Default direction
                'path': None,
                'letter': letter,
                'color': color,
                'algorithm': ghost_type,
                'lock': threading.Lock(),  # Lock for thread safety
                'last_move_time': time.time()  # Track when the ghost last moved
            }

        self.initial_ghost_positions.add(pos)    
        
        # Game status
        self.game_over = False
        self.win = False
        self.score = 0
        self.moves = 0
        
        # Track collected haunted points
        self.collected_haunted = set()
        
        # Timer for move cooldown
        self.last_move_time = time.time()
        self.move_cooldown = PLAYER_MOVEMENT  # 0.2 seconds between moves
        
        # Frame rate control
        self.last_frame_time = time.time()
        self.frame_count = 0
        self.fps = 0
        self.fps_update_time = time.time()
        
        # Lock for thread safety
        self.game_lock = threading.Lock()
        
        # Ghost threads
        self.ghost_threads = {}
        
        # Display settings
        self.show_fps = True  # Hiển thị FPS trên màn hình

    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_map(self):
        """Display the game map with colored entities"""
        self.clear_screen()
        
        # Update FPS counter
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.fps_update_time >= 1.0:  # Cập nhật FPS mỗi giây
            self.fps = self.frame_count / (current_time - self.fps_update_time)
            self.frame_count = 0
            self.fps_update_time = current_time
        
        # Print the colored map
        print("\nPacman Game:")
        if self.show_fps:
            print(f"FPS: {self.fps:.1f}")
        print("=" * 40)
        
        for y, row in enumerate(self.map_display):
            line = ""
            for x, cell in enumerate(row):
                pos = (x, y)
                
                # Player position
                if pos == self.player_pos:
                    line += Back.GREEN + 'P' + Style.RESET_ALL
                # Ghost positions
                elif any(pos == ghost['pos'] for ghost in self.ghosts.values()):
                    ghost_info = next((g for g in self.ghosts.values() if g['pos'] == pos), None)
                    line += ghost_info['color'] + ghost_info['letter'] + Style.RESET_ALL
                # Haunted points
                elif pos in self.game_map.haunted_points:
                    line += Back.MAGENTA + 'H' + Style.RESET_ALL
                # Walls
                elif cell == '#':
                    line += Back.WHITE + Fore.BLACK + '#' + Style.RESET_ALL
                # Regular cells
                else:
                    line += cell
            print(line)
        
        # Print game info
        print("=" * 40)
        print(f"Moves: {self.moves} | Score: {self.score}")
        print("Controls: ↑↓←→ to move, Q to quit")
        print("=" * 40)
        
        # Print legend
        print("\nLegend:")
        print(Back.GREEN + 'P' + Style.RESET_ALL + " - Player")
        for ghost_type, ghost in self.ghosts.items():
            print(ghost['color'] + ghost['letter'] + Style.RESET_ALL + f" - {ghost['algorithm']} Ghost")
        print(Back.MAGENTA + 'H' + Style.RESET_ALL + " - Haunted Point")
        print(Back.WHITE + Fore.BLACK + '#' + Style.RESET_ALL + " - Wall")

    def is_valid_move(self, pos):
        """Check if a position is a valid move (not a wall and within bounds)"""
        x, y = pos
        if x < 0 or x >= self.game_map.width or y < 0 or y >= self.game_map.height:
            return False
        
        return self.game_map.layout[y][x] != '#'
    
    def can_move_now(self):
        """Check if enough time has passed since the last move"""
        current_time = time.time()
        if current_time - self.last_move_time >= self.move_cooldown:
            return True
        return False
    
    def move_player(self, direction):
        """Move the player in the given direction if possible"""
        # Check if enough time has passed since last move
        if not self.can_move_now():
            return False
            
        dx, dy = direction
        new_pos = (self.player_pos[0] + dx, self.player_pos[1] + dy)
        
        if self.is_valid_move(new_pos):
            with self.game_lock:
                # Update the timer for move cooldown
                self.last_move_time = time.time()
                
                # Get the original character at the player's current position
                old_x, old_y = self.player_pos
                
                # Always keep haunted points visible when player leaves them
                if self.player_pos in self.game_map.haunted_points:
                    self.map_display[old_y][old_x] = 'H'
                else:
                    # Restore original space
                    self.map_display[old_y][old_x] = ' '
                
                # Update player position
                self.player_pos = new_pos
                self.moves += 1
            
            return True
        
        return False
    
    def ghost_movement_thread(self, ghost_type):
        """Thread function for independent ghost movement"""
        ghost = self.ghosts[ghost_type]
        
        while not self.game_over:
            current_time = time.time()
            
            # Chỉ di chuyển ma khi đã đến thời gian cập nhật
            if current_time - ghost['last_move_time'] >= GHOST_UPDATE_INTERVAL:
                # Calculate path for ghost based on current player position
                with self.game_lock:
                    current_player_pos = self.player_pos
                    current_ghost_pos = ghost['pos']
                    
                    # Get positions of all other ghosts to avoid collisions
                    other_ghost_positions = set()
                    for other_type, other_ghost in self.ghosts.items():
                        if other_type != ghost_type:  # Don't include the current ghost
                            other_ghost_positions.add(other_ghost['pos'])
                
                # Try to find a valid next position that doesn't collide with other ghosts
                max_attempts = 3  # Limit the number of path recalculations
                attempt = 0
                next_pos = None
                
                while attempt < max_attempts and next_pos is None:
                    # Choose algorithm based on ghost type
                    if ghost_type == PINK_GHOST:
                        ghost_path, _, candidate_next_pos = A_star_ghost(self.graph, current_ghost_pos, current_player_pos)
                    elif ghost_type == BLUE_GHOST:
                        ghost_path, _, candidate_next_pos = BFS_ghost(self.graph, current_ghost_pos, current_player_pos)
                    elif ghost_type == ORANGE_GHOST:
                        ghost_path, _, candidate_next_pos = DFS_ghost(self.graph, current_ghost_pos, current_player_pos)
                    elif ghost_type == RED_GHOST:
                        ghost_path, _, candidate_next_pos = UCS_ghost(self.graph, current_ghost_pos, current_player_pos)
                    
                    # Check if next position is valid (not occupied by another ghost)
                    if candidate_next_pos and candidate_next_pos not in other_ghost_positions:
                        next_pos = candidate_next_pos
                    else:
                        # If the next position is already occupied, we need to find an alternative
                        # Add a temporary obstacle at the occupied position in the graph
                        if candidate_next_pos:
                            self.graph.add_temporary_obstacle(candidate_next_pos)
                        # Increment attempt counter
                        attempt += 1
                        
                        # Small delay before trying again
                        time.sleep(0.01)  # Giảm thời gian chờ để tăng tốc độ
                
                # If we've reached max attempts but still don't have a valid next position,
                # stay in place for this turn
                if next_pos is None:
                    # Remove any temporary obstacles we added
                    if hasattr(self.graph, 'remove_all_temporary_obstacles'):
                        self.graph.remove_all_temporary_obstacles()
                        
                    # Skip this movement turn but update the last move time
                    ghost['last_move_time'] = current_time
                    time.sleep(0.01)  # Ngủ rất ngắn để giải phóng CPU
                    continue
                
                # Remove any temporary obstacles we added
                if hasattr(self.graph, 'remove_all_temporary_obstacles'):
                    self.graph.remove_all_temporary_obstacles()
                    
                # Kiểm tra xung đột vị trí tiếp theo và giải quyết
                with self.planned_positions_lock:
                    conflict = False
                    conflicting_ghost = None
                    
                    # Kiểm tra xem có ma nào đã dự định đi đến vị trí này không
                    for other_type, planned_pos in self.planned_next_positions.items():
                        if planned_pos == next_pos:
                            conflict = True
                            conflicting_ghost = other_type
                            break
                    
                    if conflict:
                        # Có xung đột - quyết định ngẫu nhiên xem ma nào được đi
                        if random.choice([True, False]):
                            # Con ma hiện tại thắng - cập nhật vị trí kế hoạch
                            self.planned_next_positions[ghost_type] = next_pos
                            # Xóa kế hoạch của con ma xung đột để nó phải tìm đường mới
                            if conflicting_ghost in self.planned_next_positions:
                                del self.planned_next_positions[conflicting_ghost]
                        else:
                            # Con ma hiện tại thua - không được đi
                            next_pos = None
                    else:
                        # Không có xung đột - lưu vị trí kế hoạch
                        self.planned_next_positions[ghost_type] = next_pos
                
                # Move ghost to next position if allowed
                if next_pos:
                    with ghost['lock']:
                        # Final check if position is still free
                        is_position_free = True
                        with self.game_lock:
                            for other_type, other_ghost in self.ghosts.items():
                                if other_type != ghost_type and other_ghost['pos'] == next_pos:
                                    is_position_free = False
                                    break
                        
                        if is_position_free:
                            # Calculate direction
                            dx = next_pos[0] - ghost['pos'][0]
                            dy = next_pos[1] - ghost['pos'][1]
                            
                            # Update ghost's previous direction
                            ghost['previous_direction'] = (dx, dy)
                            
                            # Move ghost
                            ghost['pos'] = next_pos
                            
                            # Xóa vị trí đã di chuyển khỏi kế hoạch
                            with self.planned_positions_lock:
                                if ghost_type in self.planned_next_positions:
                                    del self.planned_next_positions[ghost_type]
                
                # Check for collision with player
                with self.game_lock:
                    if ghost['pos'] == self.player_pos:
                        self.game_over = True
                
                # Cập nhật thời gian di chuyển cuối cùng
                ghost['last_move_time'] = current_time
            
            # Sleep just enough to maintain frame rate without consuming too much CPU
            time.sleep(0.01)  # Giảm thời gian chờ để tăng tốc độ phản hồi
    
    def start_ghost_threads(self):
        """Start a thread for each ghost to move independently"""
        for ghost_type in self.ghosts:
            thread = threading.Thread(target=self.ghost_movement_thread, args=(ghost_type,))
            thread.daemon = True  # Set as daemon so it exits when main thread exits
            self.ghost_threads[ghost_type] = thread
            thread.start()
    
    def check_collisions(self):
        """Check if player collided with any ghost"""
        with self.game_lock:
            for ghost in self.ghosts.values():
                if self.player_pos == ghost['pos']:
                    self.game_over = True
                    return True
            return False
    
    def play(self):
        """Main game loop"""
        self.display_map()
        
        # Start ghost threads for parallel movement
        self.start_ghost_threads()
        
        while not self.game_over:
            # Bắt đầu đo thời gian cho frame hiện tại
            frame_start_time = time.time()
            
            # Xử lý input và kiểm tra va chạm
            key_pressed = False
            
            # Kiểm tra phím nhanh hơn, không chờ lâu
            if keyboard.is_pressed('up') or keyboard.is_pressed('w'):
                key_pressed = self.move_player(UP)
            elif keyboard.is_pressed('down') or keyboard.is_pressed('s'):
                key_pressed = self.move_player(DOWN)
            elif keyboard.is_pressed('left') or keyboard.is_pressed('a'):
                key_pressed = self.move_player(LEFT)
            elif keyboard.is_pressed('right') or keyboard.is_pressed('d'):
                key_pressed = self.move_player(RIGHT)
            elif keyboard.is_pressed('q'):
                with self.game_lock:
                    self.game_over = True
                key_pressed = True
            elif keyboard.is_pressed('f'):
                # Chỉ xử lý một lần khi nhấn phím F để chuyển đổi hiển thị FPS
                if not hasattr(self, 'last_f_press') or time.time() - self.last_f_press > 0.2:
                    self.show_fps = not self.show_fps
                    self.last_f_press = time.time()
            
            # Check for collisions
            self.check_collisions()
            
            # Display updated map (chỉ cập nhật khi có hành động hoặc theo khoảng thời gian nhất định)
            if key_pressed or time.time() - self.last_frame_time >= FRAME_TIME:
                self.display_map()
                self.last_frame_time = time.time()
            
            # Check if game is over
            if self.game_over:
                if self.win:
                    print("\nYou Win! 🎮")
                else:
                    print("\nGame Over! Ghost got you! 👻")
                
                print(f"Final Score: {self.score}")
                print(f"Moves Made: {self.moves}")
                break
            
            # Tính toán thời gian đã trôi qua trong frame này
            frame_time_elapsed = time.time() - frame_start_time
            
            # Chờ thời gian cần thiết để đạt đến target FPS
            sleep_time = max(0, FRAME_TIME - frame_time_elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

# Run the game if this file is executed directly
if __name__ == "__main__":
    # Try to install keyboard if not available
    try:
        import keyboard
    except ImportError:
        print("Installing required package: keyboard")
        os.system("pip install keyboard")
        import keyboard
    
    try:
        game = GamePlay()
        game.play()
    except KeyboardInterrupt:
        print("\nGame terminated by user.")
    except Exception as e:
        print(f"An error occurred: {e}")