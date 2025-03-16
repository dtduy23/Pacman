import pygame
import sys
import time
import threading
from specification import *
from game_map import Map
from map_implement import MapGraph
from algorithm import UCS_ghost, BFS_ghost, DFS_ghost, A_star_ghost
import random
import pygame
import os

class PacmanGame2D:
    def __init__(self, map_dir=MAP_DIR):
        # Khởi tạo pygame
        pygame.init()
        pygame.display.set_caption("Pacman Game 2D")
        
        # Tải dữ liệu game
        self.game_map = Map.load_map(map_dir)
        if not self.game_map:
            print("Error loading map!")
            exit(1)
        
        # Tính toán kích thước cửa sổ dựa trên kích thước bản đồ
        self.cell_size = 30  # Kích thước mỗi ô (pixel)
        self.window_width = self.game_map.width * self.cell_size
        self.window_height = self.game_map.height * self.cell_size + 100  # Thêm không gian cho thông tin
        
        # Tạo cửa sổ game
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        self.clock = pygame.time.Clock()
        
        # Tạo đồ thị cho thuật toán tìm đường
        self.graph = MapGraph(self.game_map)
        
        # Vị trí người chơi
        self.player_pos = self.game_map.player_pos
        
        # Theo dõi các vị trí kế hoạch để tránh va chạm
        self.planned_next_positions = {}
        self.planned_positions_lock = threading.Lock()
        
        # Khởi tạo vị trí ma
        self.ghosts = {}
        self.initial_ghost_positions = set()
        
        for ghost_type, pos in self.game_map.ghost_positions.items():
            # Xác định màu dựa vào loại ma
            if ghost_type == BLUE_GHOST:
                color = (0, 255, 255)  # Cyan
            elif ghost_type == ORANGE_GHOST:
                color = (255, 165, 0)  # Orange
            elif ghost_type == RED_GHOST:
                color = (255, 0, 0)    # Red
            elif ghost_type == PINK_GHOST:
                color = (255, 192, 203) # Pink
            
            self.ghosts[ghost_type] = {
                'pos': pos,
                'previous_direction': UP,  # Hướng mặc định ban đầu
                'path': None,
                'color': color,
                'algorithm': ghost_type,
                'lock': threading.Lock(),
                'last_move_time': time.time(),
                'has_moved': False,
                'movement_type': STRAIGHT_MOVEMENT,
                'update_interval': STRAIGHT * BASE_GHOST_UPDATE_INTERVAL,
                'haunted_steps_remaining': 0,
                'is_haunted': False
            }
            
            # Lưu vị trí ban đầu
            self.initial_ghost_positions.add(pos)
        
        # Trạng thái game
        self.game_over = False
        self.win = False
        self.score = 0
        self.moves = 0
        
        # Theo dõi các haunted point đã thu thập
        self.collected_haunted = set()
        
        # Thời gian cho di chuyển người chơi
        self.last_move_time = time.time()
        self.move_cooldown = PLAYER_MOVEMENT
        
        # Kiểm soát FPS
        self.last_frame_time = time.time()
        self.frame_count = 0
        self.fps = 0
        self.fps_update_time = time.time()
        
        # Lock cho thread safety
        self.game_lock = threading.Lock()
        
        # Thread cho ma
        self.ghost_threads = {}

        # Tài nguyên hình ảnh
        self.load_images()
        
        # Font cho text
        self.font = pygame.font.SysFont('Arial', 20)
        self.small_font = pygame.font.SysFont('Arial', 16)

        # Thêm biến cho hoạt hình
        self.animation_frame = 0
        self.animation_speed = 0.2  # Tốc độ hoạt hình (giây)
        self.last_animation_time = time.time()
        
        # Tải hoạt hình cho Pacman (nếu có)
        self.pacman_animation = []

        # Thêm theo dõi các điểm (dấu chấm)
        self.points = set()
        
        # Tìm và lưu vị trí các điểm từ map
        for y, row in enumerate(self.game_map.layout):
            for x, cell in enumerate(row):
                pos = (x, y)
                if cell == '.':
                    self.points.add(pos)
        
        # Điểm đã thu thập
        self.collected_points = set()
    
    def load_images(self):
        """Tải hình ảnh thực tế cho game"""
        try:
            # Đường dẫn đến thư mục assets
            assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
            
            # Tải và scale hình ảnh người chơi (Pacman)
            pacman_path = os.path.join(assets_dir, "pacman.png")
            if os.path.exists(pacman_path):
                pacman = pygame.image.load(pacman_path).convert_alpha()
                self.player_img = pygame.transform.scale(pacman, (self.cell_size - 4, self.cell_size - 4))
            else:
                # Fallback nếu không tìm thấy file
                self.player_img = pygame.Surface((self.cell_size - 4, self.cell_size - 4), pygame.SRCALPHA)
                pygame.draw.circle(self.player_img, (255, 255, 0), 
                                (self.player_img.get_width()//2, self.player_img.get_height()//2), 
                                self.player_img.get_width()//2)
                # Vẽ miệng cho Pacman
                mouth_angle = 45  # Góc miệng mở
                pygame.draw.polygon(self.player_img, (0, 0, 0), [
                    (self.player_img.get_width()//2, self.player_img.get_height()//2),
                    (self.player_img.get_width(), self.player_img.get_height()//2 - mouth_angle//2),
                    (self.player_img.get_width(), self.player_img.get_height()//2 + mouth_angle//2)
                ])
            
            # Ma - tải hình ảnh cho từng loại ma
            self.ghost_imgs = {}
            for ghost_type, ghost in self.ghosts.items():
                # Xác định file hình ảnh dựa vào loại ma
                if ghost_type == BLUE_GHOST:
                    ghost_file = "ghost_blue.png"
                elif ghost_type == ORANGE_GHOST:
                    ghost_file = "ghost_orange.png"
                elif ghost_type == RED_GHOST:
                    ghost_file = "ghost_red.png"
                elif ghost_type == PINK_GHOST:
                    ghost_file = "ghost_pink.png"
                
                ghost_path = os.path.join(assets_dir, ghost_file)
                if os.path.exists(ghost_path):
                    ghost_img = pygame.image.load(ghost_path).convert_alpha()
                    ghost_img = pygame.transform.scale(ghost_img, (self.cell_size - 4, self.cell_size - 4))
                else:
                    # Fallback nếu không tìm thấy file
                    ghost_img = pygame.Surface((self.cell_size - 4, self.cell_size - 4), pygame.SRCALPHA)
                    pygame.draw.circle(ghost_img, ghost['color'], 
                                    (ghost_img.get_width()//2, ghost_img.get_height()//2), 
                                    ghost_img.get_width()//2)
                    # Vẽ mắt cho ma
                    eye_radius = ghost_img.get_width() // 10
                    eye_x1 = ghost_img.get_width() // 3
                    eye_x2 = ghost_img.get_width() * 2 // 3
                    eye_y = ghost_img.get_height() // 3
                    pygame.draw.circle(ghost_img, (255, 255, 255), (eye_x1, eye_y), eye_radius * 2)
                    pygame.draw.circle(ghost_img, (255, 255, 255), (eye_x2, eye_y), eye_radius * 2)
                    pygame.draw.circle(ghost_img, (0, 0, 0), (eye_x1, eye_y), eye_radius)
                    pygame.draw.circle(ghost_img, (0, 0, 0), (eye_x2, eye_y), eye_radius)
                
                self.ghost_imgs[ghost_type] = ghost_img
            
            # Tường - hình ảnh tường gạch
            wall_path = os.path.join(assets_dir, "wall.png")
            if os.path.exists(wall_path):
                wall = pygame.image.load(wall_path).convert()
                self.wall_img = pygame.transform.scale(wall, (self.cell_size, self.cell_size))
            else:
                # Fallback
                self.wall_img = pygame.Surface((self.cell_size, self.cell_size))
                self.wall_img.fill((0, 0, 150))
                # Tạo hiệu ứng gạch
                for i in range(0, self.cell_size, 4):
                    for j in range(0, self.cell_size, 8):
                        offset = 4 if i % 8 == 0 else 0
                        pygame.draw.rect(self.wall_img, (0, 0, 200), 
                                        (j + offset, i, 4, 4))
            
            # Haunted point - hình ảnh điểm ma ám
            haunted_path = os.path.join(assets_dir, "haunted.png")
            if os.path.exists(haunted_path):
                haunted = pygame.image.load(haunted_path).convert_alpha()
                self.haunted_img = pygame.transform.scale(haunted, (self.cell_size - 10, self.cell_size - 10))
            else:
                # Fallback
                self.haunted_img = pygame.Surface((self.cell_size - 10, self.cell_size - 10), pygame.SRCALPHA)
                self.haunted_img.fill((0, 0, 0, 0))  # Trong suốt
                pygame.draw.circle(self.haunted_img, (255, 0, 255), 
                                (self.haunted_img.get_width()//2, self.haunted_img.get_height()//2), 
                                self.haunted_img.get_width()//2)
            
            # Nền - có thể tải hình nền hoặc chỉ dùng màu đen
            background_path = os.path.join(assets_dir, "background.png")
            if os.path.exists(background_path):
                background = pygame.image.load(background_path).convert()
                self.background_img = pygame.transform.scale(background, (self.window_width, self.window_height))
                self.has_background = True
            else:
                self.has_background = False

            # Tải hoạt hình Pacman nếu có
            try:
                for i in range(4):  # Giả sử có 4 frame hoạt hình
                    pacman_anim_path = os.path.join(assets_dir, f"pacman_{i}.png")
                    if os.path.exists(pacman_anim_path):
                        frame = pygame.image.load(pacman_anim_path).convert_alpha()
                        frame = pygame.transform.scale(frame, (self.cell_size - 4, self.cell_size - 4))
                        self.pacman_animation.append(frame)
            except:
                # Nếu không có file hoạt hình, tạo hoạt hình đơn giản
                self.pacman_animation = []
                for i in range(4):
                    frame = pygame.Surface((self.cell_size - 4, self.cell_size - 4), pygame.SRCALPHA)
                    pygame.draw.circle(frame, (255, 255, 0), 
                                    (frame.get_width()//2, frame.get_height()//2), 
                                    frame.get_width()//2)
                    
                    # Vẽ miệng Pacman với các góc khác nhau
                    mouth_angle = 20 + i * 15  # Góc từ 20 đến 65 độ
                    pygame.draw.polygon(frame, (0, 0, 0), [
                        (frame.get_width()//2, frame.get_height()//2),
                        (frame.get_width(), frame.get_height()//2 - mouth_angle//2),
                        (frame.get_width(), frame.get_height()//2 + mouth_angle//2)
                    ])
                    self.pacman_animation.append(frame)
                
            # Điểm (dấu chấm) - hình ảnh điểm thường
            point_path = os.path.join(assets_dir, "point.png")
            if os.path.exists(point_path):
                point = pygame.image.load(point_path).convert_alpha()
                self.point_img = pygame.transform.scale(point, (self.cell_size // 4, self.cell_size // 4))
            else:
                # Fallback
                self.point_img = pygame.Surface((self.cell_size // 4, self.cell_size // 4), pygame.SRCALPHA)
                pygame.draw.circle(self.point_img, (255, 255, 255), 
                                (self.point_img.get_width()//2, self.point_img.get_height()//2), 
                                self.point_img.get_width()//2)
                
        except Exception as e:
            print(f"Error loading images: {e}")
            # Sử dụng các hình đơn giản trong trường hợp lỗi
            self.player_img = pygame.Surface((self.cell_size - 4, self.cell_size - 4), pygame.SRCALPHA)
            pygame.draw.circle(self.player_img, (255, 255, 0), 
                            (self.player_img.get_width()//2, self.player_img.get_height()//2), 
                            self.player_img.get_width()//2)
            
            self.ghost_imgs = {}
            for ghost_type, ghost in self.ghosts.items():
                ghost_img = pygame.Surface((self.cell_size - 4, self.cell_size - 4), pygame.SRCALPHA)
                pygame.draw.circle(ghost_img, ghost['color'], 
                                (ghost_img.get_width()//2, ghost_img.get_height()//2), 
                                ghost_img.get_width()//2)
                self.ghost_imgs[ghost_type] = ghost_img
            
            self.wall_img = pygame.Surface((self.cell_size, self.cell_size))
            self.wall_img.fill((0, 0, 150))
            
            self.haunted_img = pygame.Surface((self.cell_size - 10, self.cell_size - 10))
            self.haunted_img.fill((255, 0, 255))
            
            self.has_background = False
            
            # Thêm point vào fallback
            self.point_img = pygame.Surface((self.cell_size // 4, self.cell_size // 4), pygame.SRCALPHA)
            pygame.draw.circle(self.point_img, (255, 255, 255), 
                            (self.point_img.get_width()//2, self.point_img.get_height()//2), 
                            self.point_img.get_width()//2)
    
    def can_move_now(self):
        """Kiểm tra có thể di chuyển chưa"""
        current_time = time.time()
        if current_time - self.last_move_time >= self.move_cooldown:
            return True
        return False
    
    def is_valid_move(self, pos):
        """Kiểm tra di chuyển có hợp lệ không"""
        x, y = pos
        if x < 0 or x >= self.game_map.width or y < 0 or y >= self.game_map.height:
            return False
        
        return self.game_map.layout[y][x] != '#'
    
    def move_player(self, direction):
        """Di chuyển người chơi theo hướng được chỉ định"""
        if not self.can_move_now():
            return False
            
        dx, dy = direction
        new_pos = (self.player_pos[0] + dx, self.player_pos[1] + dy)
        
        if self.is_valid_move(new_pos):
            with self.game_lock:
                # Cập nhật thời gian di chuyển
                self.last_move_time = time.time()
                
                # Cập nhật vị trí người chơi
                self.player_pos = new_pos
                self.moves += 1
                
                # Lưu hướng di chuyển để xoay Pacman
                self.player_direction = direction
                
                # Kiểm tra xem đã thu thập điểm thường chưa
                if new_pos in self.points and new_pos not in self.collected_points:
                    self.collected_points.add(new_pos)
                    self.score += 1
                
                # Kiểm tra xem đã thu thập haunted point chưa (haunted points không biến mất)
                if new_pos in self.game_map.haunted_points:
                    if new_pos not in self.collected_haunted:
                        self.collected_haunted.add(new_pos)
                        self.score += 10
                
                # Kiểm tra chiến thắng - thu thập hết các điểm thường
                if len(self.collected_points) == len(self.points):
                    self.win = True
                    self.game_over = True
            
            return True
        
        return False
    
    def ghost_movement_thread(self, ghost_type):
        """Thread để điều khiển di chuyển của ma"""
        ghost = self.ghosts[ghost_type]
        
        while not self.game_over:
            current_time = time.time()
            
            # Chỉ di chuyển ma khi đến thời gian
            if current_time - ghost['last_move_time'] >= ghost['update_interval']:
                # Calculate path for ghost based on current player position
                with self.game_lock:
                    current_player_pos = self.player_pos
                    current_ghost_pos = ghost['pos']
                    
                    # Lấy vị trí của các ma khác để tránh va chạm
                    other_ghost_positions = set()
                    for other_type, other_ghost in self.ghosts.items():
                        if other_type != ghost_type:  # Không bao gồm ma hiện tại
                            other_ghost_positions.add(other_ghost['pos'])
                
                # Tìm vị trí tiếp theo hợp lệ
                max_attempts = 3
                attempt = 0
                next_pos = None
                
                while attempt < max_attempts and next_pos is None:
                    # Chọn thuật toán dựa vào loại ma
                    if ghost_type == PINK_GHOST:
                        ghost_path, _, candidate_next_pos = A_star_ghost(self.graph, current_ghost_pos, current_player_pos)
                    elif ghost_type == BLUE_GHOST:
                        ghost_path, _, candidate_next_pos = BFS_ghost(self.graph, current_ghost_pos, current_player_pos)
                    elif ghost_type == ORANGE_GHOST:
                        ghost_path, _, candidate_next_pos = DFS_ghost(self.graph, current_ghost_pos, current_player_pos)
                    elif ghost_type == RED_GHOST:
                        ghost_path, _, candidate_next_pos = UCS_ghost(self.graph, current_ghost_pos, current_player_pos)
                    
                    # Kiểm tra vị trí có hợp lệ không
                    if candidate_next_pos and candidate_next_pos not in other_ghost_positions:
                        next_pos = candidate_next_pos
                    else:
                        # Nếu vị trí đã bị chiếm, tìm đường đi khác
                        if candidate_next_pos:
                            self.graph.add_temporary_obstacle(candidate_next_pos)
                        attempt += 1
                        time.sleep(0.01)
                
                # Nếu không tìm được vị trí hợp lệ, bỏ qua lượt này
                if next_pos is None:
                    if hasattr(self.graph, 'remove_all_temporary_obstacles'):
                        self.graph.remove_all_temporary_obstacles()
                    ghost['last_move_time'] = current_time
                    time.sleep(0.01)
                    continue
                
                # Xóa chướng ngại vật tạm thời
                if hasattr(self.graph, 'remove_all_temporary_obstacles'):
                    self.graph.remove_all_temporary_obstacles()
                
                # Kiểm tra xung đột vị trí kế hoạch
                with self.planned_positions_lock:
                    conflict = False
                    conflicting_ghost = None
                    
                    for other_type, planned_pos in self.planned_next_positions.items():
                        if planned_pos == next_pos:
                            conflict = True
                            conflicting_ghost = other_type
                            break
                    
                    if conflict:
                        # Giải quyết xung đột ngẫu nhiên
                        if random.choice([True, False]):
                            self.planned_next_positions[ghost_type] = next_pos
                            if conflicting_ghost in self.planned_next_positions:
                                del self.planned_next_positions[conflicting_ghost]
                        else:
                            next_pos = None
                    else:
                        # Không có xung đột
                        self.planned_next_positions[ghost_type] = next_pos
                
                # Di chuyển ma đến vị trí tiếp theo nếu được phép
                if next_pos:
                    with ghost['lock']:
                        # Kiểm tra cuối cùng xem vị trí còn trống không
                        is_position_free = True
                        with self.game_lock:
                            for other_type, other_ghost in self.ghosts.items():
                                if other_type != ghost_type and other_ghost['pos'] == next_pos:
                                    is_position_free = False
                                    break
                        
                        if is_position_free:
                            # Lưu vị trí cũ
                            old_pos = ghost['pos']
                            
                            # Tính hướng di chuyển
                            dx = next_pos[0] - ghost['pos'][0]
                            dy = next_pos[1] - ghost['pos'][1]
                            new_direction = (dx, dy)
                            
                            # Kiểm tra xem vị trí mới có phải là haunted point không (vẫn giữ H)
                            if next_pos in self.game_map.haunted_points:
                                ghost['is_haunted'] = True
                                ghost['haunted_steps_remaining'] = HAUNTED_POINT_INDEX
                                ghost['update_interval'] = STRAIGHT * BASE_GHOST_UPDATE_INTERVAL
                            else:
                                # Nếu đang bị ám, giảm số bước còn lại
                                if ghost['haunted_steps_remaining'] > 0:
                                    ghost['haunted_steps_remaining'] -= 1
                                    ghost['update_interval'] = STRAIGHT * BASE_GHOST_UPDATE_INTERVAL
                                else:
                                    # Nếu hết bị ám, tính tốc độ dựa trên loại di chuyển
                                    ghost['is_haunted'] = False
                                    
                                    # Xác định loại di chuyển
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
                                    
                                    ghost['movement_type'] = movement_type
                            
                            # Cập nhật hướng của ma
                            ghost['previous_direction'] = new_direction
                            
                            # Di chuyển ma
                            ghost['pos'] = next_pos
                            
                            # Nếu đây là lần di chuyển đầu tiên, đánh dấu
                            if not ghost['has_moved']:
                                ghost['has_moved'] = True
                            
                            # Xóa vị trí khỏi kế hoạch
                            with self.planned_positions_lock:
                                if ghost_type in self.planned_next_positions:
                                    del self.planned_next_positions[ghost_type]
                
                # Kiểm tra va chạm với người chơi
                with self.game_lock:
                    if ghost['pos'] == self.player_pos:
                        self.game_over = True
                
                # Cập nhật thời gian di chuyển cuối
                ghost['last_move_time'] = current_time
            
            # Ngủ ngắn để tiết kiệm CPU
            time.sleep(0.01)
    
    def start_ghost_threads(self):
        """Khởi động thread cho từng con ma"""
        for ghost_type in self.ghosts:
            thread = threading.Thread(target=self.ghost_movement_thread, args=(ghost_type,))
            thread.daemon = True
            self.ghost_threads[ghost_type] = thread
            thread.start()
    
    def check_collisions(self):
        """Kiểm tra va chạm giữa người chơi và ma"""
        with self.game_lock:
            for ghost in self.ghosts.values():
                if self.player_pos == ghost['pos']:
                    self.game_over = True
                    return True
            return False
    
    def draw(self):
        """Vẽ game lên màn hình"""
        # Xóa màn hình
        self.screen.fill((0, 0, 0))
        
        # Vẽ bản đồ
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                pos = (x, y)
                screen_x = x * self.cell_size
                screen_y = y * self.cell_size
                
                # Vẽ tường
                if self.game_map.layout[y][x] == '#':
                    self.screen.blit(self.wall_img, (screen_x, screen_y))
                
                # Vẽ haunted points
                elif pos in self.game_map.haunted_points:
                    self.screen.blit(self.haunted_img, 
                                  (screen_x + (self.cell_size - self.haunted_img.get_width())//2, 
                                   screen_y + (self.cell_size - self.haunted_img.get_height())//2))
                
                # Vẽ điểm thường (chỉ nếu chưa thu thập)
                elif pos in self.points and pos not in self.collected_points:
                    self.screen.blit(self.point_img, 
                                  (screen_x + (self.cell_size - self.point_img.get_width())//2, 
                                   screen_y + (self.cell_size - self.point_img.get_height())//2))
        
        # Cập nhật hoạt hình chỉ khi có frames hoạt hình
        current_time = time.time()
        if self.pacman_animation and current_time - self.last_animation_time >= self.animation_speed:
            self.animation_frame = (self.animation_frame + 1) % len(self.pacman_animation)
            self.last_animation_time = current_time
        
        # Vẽ người chơi với hoạt hình
        player_screen_x = self.player_pos[0] * self.cell_size + (self.cell_size - self.player_img.get_width())//2
        player_screen_y = self.player_pos[1] * self.cell_size + (self.cell_size - self.player_img.get_height())//2
        
        # Xác định hướng để xoay Pacman
        if hasattr(self, 'player_direction'):
            angle = 0
            if self.player_direction == LEFT:
                angle = 180
            elif self.player_direction == UP:
                angle = 90
            elif self.player_direction == DOWN:
                angle = 270
            
            # Xoay hoạt hình theo hướng di chuyển
            if self.pacman_animation:
                rotated_frame = pygame.transform.rotate(self.pacman_animation[self.animation_frame], angle)
                self.screen.blit(rotated_frame, (player_screen_x, player_screen_y))
            else:
                rotated_img = pygame.transform.rotate(self.player_img, angle)
                self.screen.blit(rotated_img, (player_screen_x, player_screen_y))
        else:
            # Nếu không có hướng, sử dụng hình mặc định
            self.screen.blit(self.player_img, (player_screen_x, player_screen_y))
        
        # Vẽ các con ma
        for ghost_type, ghost in self.ghosts.items():
            ghost_screen_x = ghost['pos'][0] * self.cell_size + (self.cell_size - self.ghost_imgs[ghost_type].get_width())//2
            ghost_screen_y = ghost['pos'][1] * self.cell_size + (self.cell_size - self.ghost_imgs[ghost_type].get_height())//2
            
            # Nếu ma đang bị ám, thêm hiệu ứng nhấp nháy
            if ghost.get('is_haunted', False):
                # Tạo hiệu ứng nhấp nháy với alpha thay đổi
                alpha = 128 + int(127 * abs(time.time() % 1 - 0.5) / 0.5)  # Dao động từ 128-255
                ghost_img_copy = self.ghost_imgs[ghost_type].copy()
                ghost_img_copy.set_alpha(alpha)
                self.screen.blit(ghost_img_copy, (ghost_screen_x, ghost_screen_y))
            else:
                self.screen.blit(self.ghost_imgs[ghost_type], (ghost_screen_x, ghost_screen_y))
        
        # Vẽ thông tin game bên dưới bản đồ
        info_y = self.game_map.height * self.cell_size + 10
        
        # FPS
        fps_text = self.font.render(f"FPS: {self.fps:.1f}", True, (255, 255, 255))
        self.screen.blit(fps_text, (10, info_y))
        
        # Score & Moves & Points
        score_text = self.font.render(f"Score: {self.score} | Moves: {self.moves} | Points: {len(self.collected_points)}/{len(self.points)}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, info_y + 30))
        
        # Thông tin về tốc độ ma
        ghost_info_y = info_y + 60
        for i, (ghost_type, ghost) in enumerate(self.ghosts.items()):
            movement_names = {
                STRAIGHT_MOVEMENT: "Straight",
                TURN_MOVEMENT: "Turn",
                BACK_MOVEMENT: "Back"
            }
            movement_type = ghost.get('movement_type', STRAIGHT_MOVEMENT)
            move_str = movement_names.get(movement_type, "Unknown")
            
            # Màu văn bản giống màu ma
            ghost_color = ghost['color']
            
            # Thông tin ma
            ghost_text = self.small_font.render(
                f"{ghost_type}: {move_str} {ghost.get('update_interval', 0):.2f}s" + 
                (f" (Haunted: {ghost.get('haunted_steps_remaining', 0)})" if ghost.get('is_haunted', False) else ""), 
                True, ghost_color
            )
            self.screen.blit(ghost_text, (10 + i * 150, ghost_info_y))
        
        # Hiển thị màn hình game over
        if self.game_over:
            self.draw_game_over()
        
        # Cập nhật màn hình
        pygame.display.flip()
    
    def draw_game_over(self):
        """Vẽ màn hình game over"""
        # Tạo surface bán trong suốt che phủ toàn màn hình
        overlay = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # RGBA với alpha 180 (bán trong suốt)
        self.screen.blit(overlay, (0, 0))
        
        # Tạo font lớn cho thông báo
        large_font = pygame.font.SysFont('Arial', 48, bold=True)
        
        # Hiển thị thông báo game over hoặc victory
        if self.win:
            text = large_font.render("YOU WIN!", True, (0, 255, 0))
        else:
            text = large_font.render("GAME OVER", True, (255, 0, 0))
        
        # Vị trí văn bản ở giữa màn hình
        text_rect = text.get_rect(center=(self.window_width/2, self.window_height/2 - 40))
        self.screen.blit(text, text_rect)
        
        # Hiển thị điểm số và số điểm đã thu thập
        score_font = pygame.font.SysFont('Arial', 36)
        score_text = score_font.render(f"Score: {self.score} | Points: {len(self.collected_points)}/{len(self.points)}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.window_width/2, self.window_height/2 + 20))
        self.screen.blit(score_text, score_rect)
        
        # Hướng dẫn để chơi lại
        restart_font = pygame.font.SysFont('Arial', 24)
        restart_text = restart_font.render("Press SPACE to play again or ESC to quit", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(self.window_width/2, self.window_height/2 + 70))
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        """Chạy vòng lặp chính của game"""
        # Bắt đầu thread cho ma
        self.start_ghost_threads()
        
        # Vòng lặp chính
        running = True
        while running:
            # Bắt đầu tính thời gian frame
            frame_start = time.time()
            
            # Xử lý các sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # Xử lý khi game over
                    if self.game_over:
                        if event.key == pygame.K_SPACE:
                            # Khởi tạo lại game
                            self.__init__()
                        elif event.key == pygame.K_ESCAPE:
                            running = False
            
            # Xử lý phím nhấn (nếu game đang chạy)
            if not self.game_over:
                keys = pygame.key.get_pressed()
                
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    self.move_player(UP)
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    self.move_player(DOWN)
                elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.move_player(LEFT)
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.move_player(RIGHT)
                elif keys[pygame.K_q]:
                    self.game_over = True
                
                # Kiểm tra va chạm
                self.check_collisions()
            
            # Cập nhật FPS
            self.frame_count += 1
            current_time = time.time()
            if current_time - self.fps_update_time >= 1.0:
                self.fps = self.frame_count / (current_time - self.fps_update_time)
                self.frame_count = 0
                self.fps_update_time = current_time
            
            # Vẽ game
            self.draw()
            
            # Duy trì FPS ổn định
            frame_time = time.time() - frame_start
            sleep_time = max(0, FRAME_TIME - frame_time)
            time.sleep(sleep_time)
            self.clock.tick(TARGET_FPS)
        
        # Đóng game
        pygame.quit()
        sys.exit()

# Khởi chạy game nếu chạy trực tiếp
if __name__ == "__main__":
    game = PacmanGame2D()
    game.run()

# Trong class Map (game_map.py)
def load_map(cls, file_path):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        layout = []
        player_pos = None
        ghost_positions = {}
        haunted_points = set()
        
        for y, line in enumerate(lines):
            row = []
            for x, char in enumerate(line.strip()):
                # Xử lý các ký tự đặc biệt
                if char == 'P':
                    player_pos = (x, y)
                    row.append(' ')  # Thay vị trí player bằng ô trống
                elif char in ['B', 'R', 'O', 'N']:  # Các loại ma
                    if char == 'B':
                        ghost_type = BLUE_GHOST
                    elif char == 'R':
                        ghost_type = RED_GHOST
                    elif char == 'O':
                        ghost_type = ORANGE_GHOST
                    elif char == 'N':
                        ghost_type = PINK_GHOST
                    
                    ghost_positions[ghost_type] = (x, y)
                    row.append(' ')  # Thay vị trí ma bằng ô trống
                elif char == 'H':
                    haunted_points.add((x, y))
                    row.append(char)
                else:
                    row.append(char)  # Các ký tự khác giữ nguyên (bao gồm '.')
            
            layout.append(row)
        
        # Tạo thực thể map
        map_obj = cls()
        map_obj.layout = layout
        map_obj.width = len(layout[0])
        map_obj.height = len(layout)
        map_obj.player_pos = player_pos
        map_obj.ghost_positions = ghost_positions
        map_obj.haunted_points = haunted_points
        
        return map_obj
    
    except Exception as e:
        print(f"Error loading map from {file_path}: {e}")
        return None
