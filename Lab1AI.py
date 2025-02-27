import pygame
import numpy as np
import random

# Colors (RGB format)
CELL_ALIVE = (0, 200, 0)   # Green for alive cells
CELL_DEAD = (60, 60, 60)   # Dark gray for dead cells
BG_COLOR = (10, 10, 10)    # Black background
GRID_COLOR = (30, 30, 30)  # Grid lines

class CellularAutomaton:
    def __init__(self, cols, rows, cell_size):
        """
        Initializes the grid and parameters.
        """
        self.cols = cols
        self.rows = rows
        self.cell_size = cell_size
        self.grid = np.zeros((self.rows, self.cols), dtype=int)
        self.history = []
        self.generate_random_grid()

    def generate_random_grid(self):
        """
        Generates a random starting configuration.
        """
        self.grid = np.random.choice([0, 1], size=(self.rows, self.cols), p=[0.85, 0.15])
        self.history = []

    def apply_preset(self, preset):
        """
        Loads a predefined pattern.
        """
        self.grid.fill(0)
        start_x = (self.cols - len(preset[0])) // 2
        start_y = (self.rows - len(preset)) // 2
        for i, row in enumerate(preset):
            for j, value in enumerate(row):
                self.grid[start_y + i, start_x + j] = value
        self.history = []

    def count_live_neighbors(self, x, y):
        """
        Counts the number of live neighbors for a given cell.
        """
        offsets = [(-1, -1), (-1, 0), (-1, 1),
                   (0, -1),         (0, 1),
                   (1, -1), (1, 0), (1, 1)]
        
        count = sum(self.grid[x + dx, y + dy] 
                    for dx, dy in offsets 
                    if 0 <= x + dx < self.rows and 0 <= y + dy < self.cols)
        return count

    def update_grid(self):
        """
        Updates the grid based on the rules of Conway's Game of Life.
        """
        new_state = np.zeros_like(self.grid)

        for x in range(self.rows):
            for y in range(self.cols):
                neighbors = self.count_live_neighbors(x, y)
                
                if self.grid[x, y] == 1:
                    if 2 <= neighbors <= 3:  
                        new_state[x, y] = 1  # Stays alive
                else:
                    if neighbors == 3:
                        new_state[x, y] = 1  # Becomes alive

        self.history.append(self.grid.copy())
        if len(self.history) > 10:
            self.history.pop(0)

        self.grid = new_state

    def check_state(self):
        """
        Determines if the grid has reached a stable, extinct, or oscillating state.
        """
        if np.sum(self.grid) == 0:
            return "Extinct"
        if len(self.history) > 1 and np.array_equal(self.grid, self.history[-2]):
            return "Stable"
        if self.grid.tolist() in [h.tolist() for h in self.history[:-1]]:
            return "Oscillating"
        return "Evolving"

    def draw(self, screen):
        """
        Draws the current grid state.
        """
        for x in range(self.rows):
            for y in range(self.cols):
                rect = (y * self.cell_size, x * self.cell_size, self.cell_size - 1, self.cell_size - 1)
                color = CELL_ALIVE if self.grid[x, y] == 1 else CELL_DEAD
                pygame.draw.rect(screen, color, rect)

        # Draw grid lines
        for x in range(0, self.cols * self.cell_size, self.cell_size):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, self.rows * self.cell_size))
        for y in range(0, self.rows * self.cell_size, self.cell_size):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (self.cols * self.cell_size, y))

def run_simulation():
    pygame.init()
    win_size = (800, 600)
    cell_size = 20
    cols = win_size[0] // cell_size
    rows = win_size[1] // cell_size

    screen = pygame.display.set_mode(win_size)
    pygame.display.set_caption("Cellular Automaton")
    clock = pygame.time.Clock()

    sim = CellularAutomaton(cols, rows, cell_size)
    paused = False

    presets = {
        "glider": [[0, 1, 0], [0, 0, 1], [1, 1, 1]],
        "pulsar": [[0,0,1,1,1,0,0],[0,0,0,0,0,0,0],[1,0,0,0,0,0,1],[1,0,0,0,0,0,1],[1,0,0,0,0,0,1],[0,0,0,0,0,0,0],[0,0,1,1,1,0,0]],
        "beacon": [[1,1,0,0],[1,1,0,0],[0,0,1,1],[0,0,1,1]],
    }

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused  
                elif event.key == pygame.K_r:
                    sim.generate_random_grid()
                elif event.key == pygame.K_1:
                    sim.apply_preset(presets["glider"])
                elif event.key == pygame.K_2:
                    sim.apply_preset(presets["pulsar"])
                elif event.key == pygame.K_3:
                    sim.apply_preset(presets["beacon"])

        screen.fill(BG_COLOR)
        sim.draw(screen)
        if not paused:
            sim.update_grid()

        # Display the current state
        state_text = sim.check_state()
        font = pygame.font.SysFont(None, 30)
        text_surface = font.render(f"State: {state_text}", True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))

        pygame.display.flip()
        clock.tick(10)  

    pygame.quit()

if __name__ == '__main__':
    run_simulation()
    