import random

class GridEnvironment:
    def __init__(self, size=20):
        self.size = size
        # 0 = Empty, -1 = Static Wall, -2 = Dynamic Obstacle
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        
        # Fixed: Removed invalid text markers
        self.obstacle_chance = 0.03  # Probability of dynamic spawn
        
        self.static_obstacles = set()
        self.dynamic_obstacles = set()

    def add_static_wall(self, start_row, col, length):
        """Creates a vertical wall for testing static obstacles"""
        for i in range(length):
            if start_row + i < self.size:
                r, c = start_row + i, col
                self.grid[r][c] = -1
                self.static_obstacles.add((r, c))

    def toggle_obstacle(self, r, c):
        """Allows manual drawing/erasing of walls"""
        if 0 <= r < self.size and 0 <= c < self.size:
            if self.grid[r][c] == -1:
                # Remove wall
                self.grid[r][c] = 0
                if (r, c) in self.static_obstacles:
                    self.static_obstacles.remove((r, c))
            else:
                # Add wall
                self.grid[r][c] = -1
                self.static_obstacles.add((r, c))

    def spawn_dynamic_obstacle(self, start, target, current_agent_pos):
        """Handles runtime events where obstacles appear randomly"""
        if random.random() < self.obstacle_chance:
            r = random.randint(0, self.size - 1)
            c = random.randint(0, self.size - 1)
            
            # Constraints: 
            # 1. Don't spawn on Start, Target, or Agent
            # 2. Don't overwrite existing Static Walls (Keep map integrity)
            safe_zone = [start, target, current_agent_pos]
            if (r, c) not in safe_zone and self.grid[r][c] == 0:
                self.grid[r][c] = -1  # Treat as wall
                self.dynamic_obstacles.add((r, c))
                return (r, c)
        return None

    def reset_grid(self):
        """Completely wipes the grid clean"""
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.static_obstacles.clear()
        self.dynamic_obstacles.clear()

    def clean_dynamic(self):
        """Removes only dynamic obstacles (Purple) but keeps Static Walls (Black)"""
        for r, c in self.dynamic_obstacles:
            # Only remove if it wasn't originally a static wall
            if (r, c) not in self.static_obstacles:
                self.grid[r][c] = 0
        self.dynamic_obstacles.clear()

    # --- ADVANCED FEATURES ---

    def random_scatter(self, coverage=0.25):
        """Scatters random walls covering X% of the grid (Chaos Mode)"""
        self.reset_grid()
        num_obstacles = int(self.size * self.size * coverage)
        for _ in range(num_obstacles):
            r, c = random.randint(0, self.size-1), random.randint(0, self.size-1)
            if self.grid[r][c] == 0:
                self.grid[r][c] = -1
                self.static_obstacles.add((r, c))

    def generate_maze(self):
        """Generates a perfect maze using Randomized DFS (Recursive Backtracker)"""
        self.reset_grid()
        # Fill grid with walls first
        for r in range(self.size):
            for c in range(self.size):
                self.grid[r][c] = -1
                self.static_obstacles.add((r, c))

        # Helper to carve paths
        def carve(r, c):
            self.grid[r][c] = 0
            if (r, c) in self.static_obstacles:
                self.static_obstacles.remove((r, c))

            # Directions: Up, Right, Down, Left (jump 2 steps to preserve walls)
            directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
            random.shuffle(directions)

            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.size and 0 <= nc < self.size and self.grid[nr][nc] == -1:
                    # Knock down the wall between current and next
                    wr, wc = r + dr // 2, c + dc // 2
                    self.grid[wr][wc] = 0
                    if (wr, wc) in self.static_obstacles:
                        self.static_obstacles.remove((wr, wc))
                    carve(nr, nc)

        # Start carving from (0,0)
        carve(0, 0)
        
        # Ensure Start (2,2) and Target (17,17) are open
        safe_spots = [(0, 0), (self.size-1, self.size-1), (2, 2), (17, 17)]
        for r, c in safe_spots:
            if 0 <= r < self.size and 0 <= c < self.size:
                self.grid[r][c] = 0
                if (r, c) in self.static_obstacles: self.static_obstacles.remove((r, c))