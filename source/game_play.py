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
import sys

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
            'last_move_time': time.time(),  # Track when the ghost last moved
            'has_moved': False,  # Track if ghost has moved from initial position
            'movement_type': STRAIGHT_MOVEMENT,  # Default movement type
            'update_interval': STRAIGHT * BASE_GHOST_UPDATE_INTERVAL,  # Initial update interval
            'haunted_steps_remaining': 0,  # Số bước di chuyển còn lại trong trạng thái haunted
            'is_haunted': False  # Trạng thái bị ám
        }

        self.initial_ghost_positions.add(pos)    
        
        # Game status
        self.game_over = False
        self.win = False
        self.score = 0
        self.moves = 0
        self.previous_map = {}
        
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
        # self.clear_screen()
        
        # Update FPS counter
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.fps_update_time >= 1.0:  # Cập nhật FPS mỗi giây
            self.fps = self.frame_count / (current_time - self.fps_update_time)
            self.frame_count = 0
            self.fps_update_time = current_time
        
        # Print the colored map
        sys.stdout.write(f"\033[1;1H\nPacman Game:")
        if self.show_fps:
           sys.stdout.write(f"\033[3;1HFPS: {self.fps:.1f}\n")
        print("=" * 23)
        
        current_map = {}  # Lưu trạng thái mới

        for y, row in enumerate(self.map_display):
            for x, cell in enumerate(row):
                sys.stdout.write("\033[?25l")
                sys.stdout.flush()
                pos = (x, y)

                # Xác định ký tự hiển thị
                if pos == self.player_pos:
                    char = Back.GREEN + 'P' + Style.RESET_ALL
                elif any(pos == ghost['pos'] for ghost in self.ghosts.values()):
                    ghost_info = next(g for g in self.ghosts.values() if g['pos'] == pos)
                    char = ghost_info['color'] + ghost_info['letter'] + Style.RESET_ALL
                elif pos in self.game_map.haunted_points:
                    char = Back.MAGENTA + 'H' + Style.RESET_ALL
                elif cell == '#':
                    char = Back.WHITE + Fore.BLACK + '#' + Style.RESET_ALL
                else:
                    char = cell  # Giữ nguyên ô không thay đổi

                current_map[pos] = char  # Lưu ký tự hiện tại vào bản đồ mới

                # Chỉ in khi có thay đổi
                if self.previous_map.get(pos) != char:
                    sys.stdout.write(f"\033[{y+5};{x+1}H{char}")  # Di chuyển con trỏ & in ký tự
                    sys.stdout.flush()

        # Cập nhật trạng thái bản đồ trước đó
        self.previous_map = current_map

        # Hiển thị thông tin game
        right_x = 40;
        sys.stdout.write(f"\033[2;{right_x}H" + "=" * 23)  
        sys.stdout.write(f"\033[3;{right_x}HMoves: {self.moves} | Score: {self.score}")
        sys.stdout.write(f"\033[4;{right_x}HControls: ↑↓←→ to move, Q to quit")
        sys.stdout.write(f"\033[5;{right_x}H" + "=" * 23)
        sys.stdout.flush()

        # Hiển thị tốc độ di chuyển của ma
        movement_names = {
            STRAIGHT_MOVEMENT: "Đi thẳng",
            TURN_MOVEMENT: "Rẽ",
            BACK_MOVEMENT: "Quay lại"
        }
        line = 8  # Dòng bắt đầu in thông tin ma
        # Hiển thị legend (chú thích ký hiệu)
        sys.stdout.write(f"\033[{line+1};{right_x}HLegend:")
        sys.stdout.write(f"\033[{line+2};{right_x}H" + Back.GREEN + 'P' + Style.RESET_ALL + " - Player")

        for ghost_type, ghost in self.ghosts.items():
            sys.stdout.write(f"\033[{line+3};{right_x}H{ghost['color']}{ghost['letter']}{Style.RESET_ALL} - {ghost['algorithm']} Ghost")
            line += 1

        sys.stdout.write(f"\033[{line+3};{right_x}H" + Back.MAGENTA + 'H' + Style.RESET_ALL + " - Haunted Point")
        sys.stdout.write(f"\033[{line+4};{right_x}H" + Back.WHITE + Fore.BLACK + '#' + Style.RESET_ALL + " - Wall")

        line += 7

        sys.stdout.write(f"\033[{line};{right_x}HTốc độ di chuyển ma:")
        line += 1
        for ghost_type, ghost in self.ghosts.items():
            movement_type = ghost.get('movement_type', STRAIGHT_MOVEMENT)
            update_interval = ghost.get('update_interval', STRAIGHT * BASE_GHOST_UPDATE_INTERVAL)
            move_str = movement_names.get(movement_type, "Unknown")

            haunted_status = ""
            if ghost.get('is_haunted', False):
                haunted_status = f" (Haunted: {ghost.get('haunted_steps_remaining', 0)} bước còn lại)      "

                sys.stdout.write(f"\033[{line};{right_x}H{ghost['color']}{ghost['letter']}{Style.RESET_ALL}: {move_str} - {update_interval:.2f}s{haunted_status}")
            line += 1

        # sys.stdout.flush()  # Cập nhật màn hình ngay

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
        
        # Đảm bảo ma có các thuộc tính cần thiết
        if 'update_interval' not in ghost:
            ghost['update_interval'] = STRAIGHT * BASE_GHOST_UPDATE_INTERVAL
        if 'movement_type' not in ghost:
            ghost['movement_type'] = STRAIGHT_MOVEMENT
        if 'previous_direction' not in ghost:
            ghost['previous_direction'] = UP  # Hướng mặc định
        if 'last_move_time' not in ghost:
            ghost['last_move_time'] = time.time()
        if 'haunted_steps_remaining' not in ghost:
            ghost['haunted_steps_remaining'] = 0
        if 'is_haunted' not in ghost:
            ghost['is_haunted'] = False
        
        while not self.game_over:
            current_time = time.time()
            
            # Kiểm tra xem đã đến lúc cập nhật chưa
            if current_time - ghost['last_move_time'] >= ghost['update_interval']:
                # Calculate path for ghost based on current player position
                with self.game_lock:
                    current_player_pos = self.player_pos
                    current_ghost_pos = ghost['pos']
                    current_direction = ghost['previous_direction']
                    
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
                            # Lưu vị trí hiện tại để sau đó xóa
                            old_pos = ghost['pos']
                            
                            # Calculate direction
                            dx = next_pos[0] - ghost['pos'][0]
                            dy = next_pos[1] - ghost['pos'][1]
                            new_direction = (dx, dy)
                            
                            # Kiểm tra xem vị trí mới có phải là haunted point không
                            if next_pos in self.game_map.haunted_points:
                                ghost['is_haunted'] = True
                                ghost['haunted_steps_remaining'] = HAUNTED_POINT_INDEX  # 10 bước
                                # Khi bị ám, di chuyển luôn với tốc độ STRAIGHT
                                ghost['update_interval'] = STRAIGHT * BASE_GHOST_UPDATE_INTERVAL
                            else:
                                # Nếu đang bị ám, giảm số bước còn lại
                                if ghost['haunted_steps_remaining'] > 0:
                                    ghost['haunted_steps_remaining'] -= 1
                                    # Vẫn giữ tốc độ STRAIGHT
                                    ghost['update_interval'] = STRAIGHT * BASE_GHOST_UPDATE_INTERVAL
                                else:
                                    # Nếu hết bị ám hoặc không bị ám, tính toán tốc độ dựa trên loại di chuyển
                                    ghost['is_haunted'] = False
                                    
                                    # Xác định loại di chuyển (thẳng, rẽ, lùi)
                                    if ghost['previous_direction'] == new_direction:
                                        movement_type = STRAIGHT_MOVEMENT
                                        ghost['update_interval'] = STRAIGHT * BASE_GHOST_UPDATE_INTERVAL
                                    elif (ghost['previous_direction'][0] == -new_direction[0] and 
                                          ghost['previous_direction'][1] == -new_direction[1]):
                                        movement_type = BACK_MOVEMENT
                                        ghost['update_interval'] = BACK * BASE_GHOST_UPDATE_INTERVAL
                                    else:
                                        movement_type = TURN_MOVEMENT
                                        ghost['update_interval'] = TURN * BASE_GHOST_UPDATE_INTERVAL
                                    
                                    # Lưu lại loại di chuyển để hiển thị
                                    ghost['movement_type'] = movement_type
                            
                            # Update ghost's previous direction
                            ghost['previous_direction'] = new_direction
                            
                            # Move ghost
                            ghost['pos'] = next_pos
                            
                            # Nếu đây là lần di chuyển đầu tiên, xóa vị trí ban đầu trên bản đồ
                            if not ghost.get('has_moved', False):
                                with self.game_lock:
                                    old_x, old_y = old_pos
                                    # Đảm bảo vị trí này không được sử dụng bởi ghost khác
                                    is_used_by_other = False
                                    for other_type, other_ghost in self.ghosts.items():
                                        if other_type != ghost_type and other_ghost['pos'] == old_pos:
                                            is_used_by_other = True
                                            break
                                    
                                    # Nếu không có ghost nào khác ở vị trí cũ, xóa nó
                                    if not is_used_by_other:
                                        # Kiểm tra xem có phải là haunted point không
                                        if old_pos in self.game_map.haunted_points:
                                            self.map_display[old_y][old_x] = 'H'
                                        else:
                                            self.map_display[old_y][old_x] = ' '
                                    
                                    # Đánh dấu đã di chuyển
                                    ghost['has_moved'] = True
                            
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
                
                # Hiển thị thông tin về loại di chuyển và khoảng thời gian (debug)
                if hasattr(self, 'show_movement_debug') and self.show_movement_debug:
                    movement_names = {
                        STRAIGHT_MOVEMENT: "Straight",
                        TURN_MOVEMENT: "Turn",
                        BACK_MOVEMENT: "Back"
                    }
                    print(f"{ghost['letter']}: {movement_names[ghost['movement_type']]} - {ghost['update_interval']:.2f}s")
            
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
                    sys.stdout.write(f"\033[7;{40}HYou Win! 🎮")
                else:
                    sys.stdout.write(f"\033[7;{40}HGame Over! Ghost got you! 👻")
                
                sys.stdout.write(f"\033[8;{40}HFinal Score: {self.score}")
                sys.stdout.write(f"\033[9;{40}HMoves Made: {self.moves}")
                input()
                break
            
            # Tính toán thời gian đã trôi qua trong frame này
            frame_time_elapsed = time.time() - frame_start_time
            
            # Chờ thời gian cần thiết để đạt đến target FPS
            sleep_time = max(0, FRAME_TIME - frame_time_elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

# Run the game if this file is executed directly
def game_text():
    os.system('cls' if os.name == 'nt' else 'clear')
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

if __name__ == "__main__":
    game_text()