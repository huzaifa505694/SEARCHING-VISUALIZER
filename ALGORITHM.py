import collections
import heapq

class SearchAlgorithms:
    def __init__(self, grid_size):
        self.grid_size = grid_size
        # Strict Clockwise Order: Up, Right, Bottom, B-Right, Left, T-Left, T-Right, B-Left [cite: 32-40]
        self.directions = [
            (-1, 0), (0, 1), (1, 0), (1, 1), 
            (0, -1), (-1, -1), (-1, 1), (1, -1)
        ]

    def get_neighbors(self, node, grid):
        neighbors = []
        r, c = node
        for dr, dc in self.directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                if grid[nr][nc] != -1: # Avoid static and dynamic walls [cite: 17, 21]
                    neighbors.append((nr, nc))
        return neighbors

    # --- 1. BFS (Already provided) ---
    def bfs(self, start, target, grid, callback):
        queue = collections.deque([start])
        visited = {start: None}
        while queue:
            current = queue.popleft()
            if current == target: return self.reconstruct_path(visited, target)
            for neighbor in self.get_neighbors(current, grid):
                if neighbor not in visited:
                    visited[neighbor] = current
                    queue.append(neighbor)
                    callback(neighbor, list(queue), visited.keys())
        return None

    # --- 2. DFS [cite: 26] ---
    def dfs(self, start, target, grid, callback):
        stack = [start]
        visited = {start: None}
        while stack:
            current = stack.pop()
            if current == target: return self.reconstruct_path(visited, target)
            for neighbor in self.get_neighbors(current, grid):
                if neighbor not in visited:
                    visited[neighbor] = current
                    stack.append(neighbor)
                    callback(neighbor, list(stack), visited.keys())
        return None

    # --- 3. UCS [cite: 27] ---
    def ucs(self, start, target, grid, callback):
        pq = [(0, start)]
        visited = {start: (0, None)}
        while pq:
            cost, current = heapq.heappop(pq)
            if current == target: return self.reconstruct_path_dict(visited, target)
            for neighbor in self.get_neighbors(current, grid):
                new_cost = cost + 1
                if neighbor not in visited or new_cost < visited[neighbor][0]:
                    visited[neighbor] = (new_cost, current)
                    heapq.heappush(pq, (new_cost, neighbor))
                    callback(neighbor, [n for c, n in pq], visited.keys())
        return None

    # --- 4. Depth-Limited Search (DLS)  ---
    def dls(self, start, target, grid, limit, callback):
        def recursive_dls(node, target, depth, visited):
            if node == target: return [node]
            if depth <= 0: return None
            
            for neighbor in self.get_neighbors(node, grid):
                if neighbor not in visited:
                    visited[neighbor] = node
                    callback(neighbor, [], visited.keys())
                    path = recursive_dls(neighbor, target, depth - 1, visited)
                    if path: return [node] + path
            return None
        
        visited = {start: None}
        return recursive_dls(start, target, limit, visited)

    # --- 5. Iterative Deepening DFS (IDDFS)  ---
    def iddfs(self, start, target, grid, max_depth, callback):
        for depth in range(max_depth):
            result = self.dls(start, target, grid, depth, callback)
            if result: return result
        return None

    # --- 6. Bidirectional Search  ---
    def bidirectional_search(self, start, target, grid, callback):
        f_queue, b_queue = collections.deque([start]), collections.deque([target])
        f_visited, b_visited = {start: None}, {target: None}

        while f_queue and b_queue:
            # Forward step
            f_curr = f_queue.popleft()
            for n in self.get_neighbors(f_curr, grid):
                if n not in f_visited:
                    f_visited[n] = f_curr
                    f_queue.append(n)
                    callback(n, list(f_queue), f_visited.keys())
                if n in b_visited: return self.join_paths(f_visited, b_visited, n)
            
            # Backward step
            b_curr = b_queue.popleft()
            for n in self.get_neighbors(b_curr, grid):
                if n not in b_visited:
                    b_visited[n] = b_curr
                    b_queue.append(n)
                    callback(n, list(b_queue), b_visited.keys())
                if n in f_visited: return self.join_paths(f_visited, b_visited, n)
        return None

    def join_paths(self, f_visited, b_visited, meeting_node):
        path_f = self.reconstruct_path(f_visited, meeting_node)
        path_b = self.reconstruct_path(b_visited, meeting_node)
        return path_f[:-1] + path_b[::-1]

    def reconstruct_path(self, visited, current):
        path = []
        while current is not None:
            path.append(current); current = visited[current]
        return path[::-1]

    def reconstruct_path_dict(self, visited, current):
        path = []
        while current is not None:
            path.append(current); current = visited[current][1]
        return path[::-1]