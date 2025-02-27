import pygame
import random
import time
import pickle  # Used to save/load the maze

# Settings
CELL_SIZE = 15
GRID_SIZE = (51, 51)
SCREEN_SIZE = (GRID_SIZE[0] * CELL_SIZE, GRID_SIZE[1] * CELL_SIZE)

# Colors
WALL_COLOR = (40, 40, 40)
PATH_COLOR = (255, 255, 255)
CURRENT_COLOR = (0, 255, 0)

# Directions (for DFS)
DIRECTIONS = [(0, -2), (0, 2), (-2, 0), (2, 0)]


class MazeGenerator:
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.maze = [[1 for _ in range(grid_size[0])] for _ in range(grid_size[1])]
        self.start = (1, 1)
        self.stack = [self.start]
        self.maze[self.start[1]][self.start[0]] = 0

    def generate_step(self):
        """
        Generates one step of the maze using DFS with backtracking.
        """
        if not self.stack:
            return False  # Maze is complete

        x, y = self.stack[-1]
        neighbors = []

        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 1 <= nx < self.grid_size[0] - 1 and 1 <= ny < self.grid_size[1] - 1 and self.maze[ny][nx] == 1:
                neighbors.append((nx, ny))

        if neighbors:
            nx, ny = random.choice(neighbors)
            wall_x, wall_y = (x + nx) // 2, (y + ny) // 2
            self.maze[wall_y][wall_x] = 0
            self.maze[ny][nx] = 0
            self.stack.append((nx, ny))
        else:
            self.stack.pop()

        return True

    def save_maze(self):
        """
        Saves the generated maze to a file.
        """
        with open("maze.pkl", "wb") as f:
            pickle.dump(self.maze, f)

    def draw(self, screen):
        """
        Draws the maze generation process.
        """
        for y in range(self.grid_size[1]):
            for x in range(self.grid_size[0]):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                color = WALL_COLOR if self.maze[y][x] == 1 else PATH_COLOR
                pygame.draw.rect(screen, color, rect)

        if self.stack:
            x, y = self.stack[-1]
            pygame.draw.rect(screen, CURRENT_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Maze Generation (DFS)")

    maze = MazeGenerator(GRID_SIZE)
    running = True

    while running:
        screen.fill((0, 0, 0))
        maze.draw(screen)
        pygame.display.update()

        if not maze.generate_step():
            maze.save_maze()  # Save the maze when finished
            time.sleep(1)  # Pause before quitting
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()


if __name__ == "__main__":
    main()
    