# AI Pathfinder - Uninformed Search Visualization 
### 🤖 AI 2002 - Assignment 01 (Spring 2026)

This project is a graphical visualization of **Uninformed Search Algorithms** in a grid environment. It demonstrates how "blind" AI agents explore a map to find a path from a **Start (S)** point to a **Target (T)** while navigating static walls and dynamic obstacles.

## 🚀 Features
* **6 Search Algorithms:** Visualizes BFS, DFS, UCS, DLS, IDDFS, and Bidirectional Search.
* **Dynamic Environment:** Obstacles have a small probability of spawning randomly *during* the search, forcing the agent to **re-plan** its path in real-time.
* **Interactive Map:** * **Draw Walls:** Click and drag to draw custom barriers.
    * **Auto Maze:** Generates a perfect maze using Recursive Backtracking.
    * **Trap Mode:** Creates a specific U-shaped trap to test DFS behavior.
* **Path Tracing:** Visualizes the specific path the agent takes (Cyan trail) vs. the calculated path (Yellow).
* **Live Metrics:** Displays "Nodes Visited" and "Path Length" in real-time.

## 🛠️ Prerequisites
* Python 3.x
* Pygame library

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/AI_A1_22F_XXXX.git](https://github.com/your-username/AI_A1_22F_XXXX.git)
    cd AI_A1_22F_XXXX
    ```

2.  **Install dependencies:**
    ```bash
    pip install pygame
    ```

## 🎮 How to Run
Run the main script to launch the **"GOOD PERFORMANCE TIME APP"**:

```bash
python main.py
