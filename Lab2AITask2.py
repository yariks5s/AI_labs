import pygame
import time
import pickle  # Used to load saved maze

# Settings
CELL_SIZE = 15
GRID_SIZE = (51, 51)
SCREEN_SIZE = (GRID_SIZE[0] * CELL_SIZE, GRID_SIZE[1] * CELL_SIZE)

# Colors
WALL_COLOR = (40, 40, 40)
PATH_COLOR = (255, 255, 255)
VISITED_COLOR = (0, 200, 255)
SOLUTION_COLOR = (255, 0, 0)
START_COLOR = (0, 255, 0)
END_COLOR = (255, 255, 0)


class MazeSolver:
    def __init__(self, maze):
        self.maze = maze
        self.start = (1, 1)
        self.end = (GRID_SIZE[0] - 2, GRID_SIZE[1] - 2)
        self.path = []
        self.queue = [self.start]
        self.visited = {self.start: None}

    def solve_step(self):
        """
        Solves the maze one step at a time using BFS.
        """
        if not self.queue:
            return False  # No solution found

        x, y = self.queue.pop(0)

        if (x, y) == self.end:
            self.reconstruct_path()
            return False  # Solution found

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 1 <= nx < GRID_SIZE[0] - 1 and 1 <= ny < GRID_SIZE[1] - 1 and self.maze[ny][nx] == 0 and (nx, ny) not in self.visited:
                self.queue.append((nx, ny))
                self.visited[(nx, ny)] = (x, y)

        return True

    def reconstruct_path(self):
        """
        Traces back from the end to reconstruct the shortest path.
        """
        current = self.end
        while current:
            self.path.append(current)
            current = self.visited.get(current)

    def draw(self, screen):
        """
        Draws the maze and the solving process.
        """
        for y in range(GRID_SIZE[1]):
            for x in range(GRID_SIZE[0]):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if (x, y) == self.start:
                    pygame.draw.rect(screen, START_COLOR, rect)
                elif (x, y) == self.end:
                    pygame.draw.rect(screen, END_COLOR, rect)
                elif (x, y) in self.path:
                    pygame.draw.rect(screen, SOLUTION_COLOR, rect)
                elif (x, y) in self.visited:
                    pygame.draw.rect(screen, VISITED_COLOR, rect)
                elif self.maze[y][x] == 1:
                    pygame.draw.rect(screen, WALL_COLOR, rect)
                else:
                    pygame.draw.rect(screen, PATH_COLOR, rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Maze Solving (BFS)")

    # Load pre-generated maze
    with open("maze.pkl", "rb") as f:
        maze = pickle.load(f)

    solver = MazeSolver(maze)
    running = True

    while running:
        screen.fill((0, 0, 0))
        solver.draw(screen)
        pygame.display.update()

        if not solver.solve_step():
            time.sleep(1)  # Pause before quitting
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()


if __name__ == "__main__":
    main()
    