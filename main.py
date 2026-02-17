import pygame
import time
from environment import GridEnvironment
from ALGORITHM import SearchAlgorithms

# --- Configuration ---
WINDOW_TITLE = "SEARCHING VISUALIZER"
GRID_SIZE = 20
CELL_SIZE = 30
GRID_PIXEL_SIZE = GRID_SIZE * CELL_SIZE
PANEL_WIDTH = 320
SCREEN_WIDTH = GRID_PIXEL_SIZE + PANEL_WIDTH
SCREEN_HEIGHT = GRID_PIXEL_SIZE

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (240, 240, 240)
GREEN = (46, 204, 113)   # Start / Active Button
BLUE = (52, 152, 219)    # Target
RED = (231, 76, 60)      # Agent
DARK_GRAY = (52, 73, 94) # Wall
PURPLE = (155, 89, 182)  # Dynamic Obstacle
ORANGE = (243, 156, 18)  # Frontier
LIGHT_BLUE = (174, 214, 241) # Explored
YELLOW = (241, 196, 15)  # Planned Path
CYAN = (0, 206, 209)     # Traced Path (The trail left behind)

# Button Styling
BTN_COLOR = (52, 73, 94)
BTN_HOVER = (44, 62, 80)
BTN_ACTIVE = (39, 174, 96) # Green for active mode
TXT_COLOR = (236, 240, 241)

class Button:
    def __init__(self, x, y, w, h, text, action_code):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action_code = action_code
        self.is_hovered = False

    def draw(self, screen, font, is_active=False):
        if is_active:
            color = BTN_ACTIVE
        else:
            color = BTN_HOVER if self.is_hovered else BTN_COLOR
            
        # Shadow
        pygame.draw.rect(screen, (149, 165, 166), (self.rect.x+3, self.rect.y+3, self.rect.w, self.rect.h), border_radius=6)
        # Button Body
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        # Border
        pygame.draw.rect(screen, (44, 62, 80), self.rect, 2, border_radius=6)
        
        text_surf = font.render(self.text, True, TXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_click(self, pos):
        return self.rect.collidepoint(pos)

class PathfinderApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        
        # Fonts
        self.header_font = pygame.font.SysFont('Segoe UI', 24, bold=True)
        self.btn_font = pygame.font.SysFont('Segoe UI', 15, bold=True)
        self.stats_font = pygame.font.SysFont('Consolas', 15) 
        self.label_font = pygame.font.SysFont('Arial', 18, bold=True)

        self.env = GridEnvironment(GRID_SIZE)
        self.algo = SearchAlgorithms(GRID_SIZE)
        
        self.start = (2, 2)
        self.target = (17, 17)
        self.current_pos = self.start
        
        # State Variables
        self.status_msg = "Ready"
        self.nodes_visited = 0
        self.path_len = 0
        self.is_dragging = False 
        self.animation_speed = 0.02 
        self.speed_label = "Fast"
        
        self.current_mode = 'WALL' 
        
        self.setup_ui()
        self.env.add_static_wall(5, 5, 10)

    def setup_ui(self):
        btn_w, btn_h = 260, 35
        btn_gap = 10
        start_y = 55
        center_x = GRID_PIXEL_SIZE + (PANEL_WIDTH - btn_w) // 2
        
        self.buttons = [
            Button(center_x, start_y, btn_w, btn_h, "1. Breadth-First (BFS)", 1),
            Button(center_x, start_y + (btn_h+btn_gap)*1, btn_w, btn_h, "2. Depth-First (DFS)", 2),
            Button(center_x, start_y + (btn_h+btn_gap)*2, btn_w, btn_h, "3. Uniform-Cost (UCS)", 3),
            Button(center_x, start_y + (btn_h+btn_gap)*3, btn_w, btn_h, "4. Depth-Limited (DLS)", 4),
            Button(center_x, start_y + (btn_h+btn_gap)*4, btn_w, btn_h, "5. Iterative Deep (IDDFS)", 5),
            Button(center_x, start_y + (btn_h+btn_gap)*5, btn_w, btn_h, "6. Bidirectional", 6),
        ]
        
        # Placement Mode Buttons
        mode_y = start_y + (btn_h+btn_gap)*6 + 15
        half_w = (btn_w - 10) // 2
        self.btn_set_start = Button(center_x, mode_y, half_w, btn_h, "Set Start (S)", 'SET_S')
        self.btn_set_target = Button(center_x + half_w + 10, mode_y, half_w, btn_h, "Set Target (T)", 'SET_T')
        self.buttons.append(self.btn_set_start)
        self.buttons.append(self.btn_set_target)

        # Control Buttons
        ctrl_y = mode_y + btn_h + 15
        self.buttons.append(Button(center_x, ctrl_y, half_w, btn_h, "Reset Map", 'R'))
        self.buttons.append(Button(center_x + half_w + 10, ctrl_y, half_w, btn_h, "Clear Dyn", 'C'))
        
        # Speed Button
        self.speed_btn = Button(center_x, ctrl_y + btn_h + 10, btn_w, btn_h, f"Speed: {self.speed_label}", 'S')
        self.buttons.append(self.speed_btn)

    def draw_grid_cell(self, r, c, color):
        rect = pygame.Rect(c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (220, 220, 220), rect, 1)
        
        if (r, c) == self.start: 
            text = self.label_font.render("S", True, WHITE)
            self.screen.blit(text, text.get_rect(center=rect.center))
        if (r, c) == self.target:
            text = self.label_font.render("T", True, WHITE)
            self.screen.blit(text, text.get_rect(center=rect.center))

    def draw_ui(self):
        self.screen.fill(WHITE)
        # 1. Draw Grid
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                color = (252, 252, 252)
                # Drawing Priority: Wall > Dyn Obstacle > Trace > Path > Frontier/Explored
                if self.env.grid[r][c] == -1:
                    color = PURPLE if (r, c) in self.env.dynamic_obstacles else DARK_GRAY
                elif (r, c) in self.traced_set: color = CYAN # The new trail color
                elif (r, c) in self.path_set: color = YELLOW
                elif (r, c) in self.explored_set: color = LIGHT_BLUE
                elif (r, c) in self.frontier_set: color = ORANGE
                
                # Overwrite for Start/Target/Agent
                if (r, c) == self.start: color = GREEN
                if (r, c) == self.target: color = BLUE
                if (r, c) == self.current_pos: color = RED
                
                self.draw_grid_cell(r, c, color)

        # 2. Side Panel
        panel_rect = pygame.Rect(GRID_PIXEL_SIZE, 0, PANEL_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, LIGHT_GRAY, panel_rect)
        pygame.draw.line(self.screen, (189, 195, 199), (GRID_PIXEL_SIZE, 0), (GRID_PIXEL_SIZE, SCREEN_HEIGHT), 2)
        
        title = self.header_font.render("Control Menu", True, (44, 62, 80))
        self.screen.blit(title, (GRID_PIXEL_SIZE + 80, 15))
        
        # Draw Buttons
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.is_hovered = btn.rect.collidepoint(mouse_pos)
            is_active = False
            if btn.action_code == 'SET_S' and self.current_mode == 'START': is_active = True
            if btn.action_code == 'SET_T' and self.current_mode == 'TARGET': is_active = True
            
            btn.draw(self.screen, self.btn_font, is_active)
            
        # Status Box
        box_x = GRID_PIXEL_SIZE + 15
        box_y = 500
        box_w = PANEL_WIDTH - 30
        box_h = 75
        pygame.draw.rect(self.screen, (200, 200, 200), (box_x+2, box_y+2, box_w, box_h), border_radius=10)
        pygame.draw.rect(self.screen, WHITE, (box_x, box_y, box_w, box_h), border_radius=10)
        pygame.draw.rect(self.screen, (180, 180, 180), (box_x, box_y, box_w, box_h), 1, border_radius=10)
        
        stats = [
            f"Status: {self.status_msg}",
            f"Nodes Visited: {self.nodes_visited}",
            f"Path Length:  {self.path_len}"
        ]
        for i, line in enumerate(stats):
            text = self.stats_font.render(line, True, (50, 50, 50)) 
            self.screen.blit(text, (box_x + 15, box_y + 10 + i*20))

        # Mode Indicator
        mode_text = f"Current Mode: {self.current_mode} Placement"
        if self.current_mode == 'WALL': mode_text = "Current Mode: Draw Walls"
        m_surf = self.stats_font.render(mode_text, True, (100, 100, 100))
        self.screen.blit(m_surf, (GRID_PIXEL_SIZE + 30, box_y - 25))

        inst_text = self.stats_font.render("Hold Click to Place | 'R' Reset", True, (100, 100, 100))
        inst_rect = inst_text.get_rect(center=(GRID_PIXEL_SIZE + PANEL_WIDTH//2, SCREEN_HEIGHT - 15))
        self.screen.blit(inst_text, inst_rect)

        pygame.display.flip()

    def handle_grid_click(self, r, c):
        if self.current_mode == 'START':
            if (r, c) != self.target and self.env.grid[r][c] != -1:
                self.start = (r, c)
                self.current_pos = (r, c)
                self.status_msg = "Start Position Set"
        elif self.current_mode == 'TARGET':
            if (r, c) != self.start and self.env.grid[r][c] != -1:
                self.target = (r, c)
                self.status_msg = "Target Position Set"
        elif self.current_mode == 'WALL':
            if (r, c) != self.start and (r, c) != self.target:
                self.env.toggle_obstacle(r, c)

    def viz_callback(self, node, frontier, explored):
        self.nodes_visited = len(explored)
        self.frontier_set = set(frontier)
        self.explored_set = set(explored)
        self.draw_ui()
        self.env.spawn_dynamic_obstacle(self.start, self.target, self.current_pos)
        time.sleep(self.animation_speed)
        pygame.event.pump()

    def move_agent(self, path):
        if not path: return
        self.path_set = set(path)
        self.path_len = len(path)
        self.status_msg = "Path Found! Tracing..."
        self.draw_ui()
        
        # Pause to show full yellow path
        time.sleep(0.5)
        
        # Start Tracing
        self.status_msg = "Moving Agent..."
        self.traced_set = set() # Start a fresh trace
        
        for i in range(1, len(path)):
            next_node = path[i]
            
            # Dynamic Re-planning Check
            if self.env.grid[next_node[0]][next_node[1]] == -1:
                self.status_msg = "BLOCKED! Re-planning..."
                time.sleep(0.5)
                return self.run_algo(self.last_algo_code)
            
            # Update Position and Trace
            self.traced_set.add(self.current_pos) # Mark previous spot as traced
            self.current_pos = next_node
            self.traced_set.add(self.current_pos) # Mark current spot as traced
            
            self.draw_ui()
            time.sleep(0.15) 
            
            if self.env.spawn_dynamic_obstacle(self.start, self.target, self.current_pos):
                self.draw_ui()
        
        self.status_msg = "Target Reached!"
        self.draw_ui()

    def run_algo(self, code):
        self.last_algo_code = code
        self.nodes_visited = 0
        self.frontier_set, self.explored_set, self.path_set = set(), set(), set()
        self.traced_set = set() # Reset trace on new run
        self.status_msg = "Searching..."
        
        if self.current_pos == self.target: self.current_pos = self.start
            
        methods = {
            1: lambda: self.algo.bfs(self.current_pos, self.target, self.env.grid, self.viz_callback),
            2: lambda: self.algo.dfs(self.current_pos, self.target, self.env.grid, self.viz_callback),
            3: lambda: self.algo.ucs(self.current_pos, self.target, self.env.grid, self.viz_callback),
            4: lambda: self.algo.dls(self.current_pos, self.target, self.env.grid, 20, self.viz_callback),
            5: lambda: self.algo.iddfs(self.current_pos, self.target, self.env.grid, 30, self.viz_callback),
            6: lambda: self.algo.bidirectional_search(self.current_pos, self.target, self.env.grid, self.viz_callback)
        }
        
        if code in methods:
            path = methods[code]()
            if path:
                self.move_agent(path)
            else:
                self.status_msg = "No Path Found!"
                self.draw_ui()

    def toggle_speed(self):
        if self.speed_label == "Fast":
            self.speed_label = "Slow"
            self.animation_speed = 0.1
        else:
            self.speed_label = "Fast"
            self.animation_speed = 0.02
        self.speed_btn.text = f"Speed: {self.speed_label}"

    def run(self):
        running = True
        self.frontier_set, self.explored_set, self.path_set, self.traced_set = set(), set(), set(), set()
        
        while running:
            self.draw_ui()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if mx < GRID_PIXEL_SIZE: 
                        self.is_dragging = True
                        r, c = my // CELL_SIZE, mx // CELL_SIZE
                        self.handle_grid_click(r, c)
                    else: 
                        for btn in self.buttons:
                            if btn.check_click((mx, my)):
                                if isinstance(btn.action_code, int): self.run_algo(btn.action_code)
                                elif btn.action_code == 'R': 
                                    self.env.reset_grid()
                                    self.current_pos = self.start
                                    self.frontier_set, self.explored_set, self.path_set, self.traced_set = set(), set(), set(), set()
                                    self.status_msg = "Map Reset"
                                    self.nodes_visited, self.path_len = 0, 0
                                elif btn.action_code == 'C': self.env.clean_dynamic()
                                elif btn.action_code == 'S': self.toggle_speed()
                                # NEW: Deselect logic added below
                                elif btn.action_code == 'SET_S': 
                                    # If already in START mode, deselect to WALL mode. Otherwise, switch to START mode.
                                    self.current_mode = 'WALL' if self.current_mode == 'START' else 'START'
                                elif btn.action_code == 'SET_T': 
                                    # If already in TARGET mode, deselect to WALL mode. Otherwise, switch to TARGET mode.
                                    self.current_mode = 'WALL' if self.current_mode == 'TARGET' else 'TARGET'

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.is_dragging = False
                
                elif event.type == pygame.MOUSEMOTION and self.is_dragging:
                    mx, my = pygame.mouse.get_pos()
                    if mx < GRID_PIXEL_SIZE:
                        r, c = my // CELL_SIZE, mx // CELL_SIZE
                        self.handle_grid_click(r, c)

if __name__ == "__main__":
    app = PathfinderApp()
    app.run()