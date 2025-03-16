import pygame # type: ignore
import random
import math
import sys


def generate_cave_map(num_caves=30, degree=3):
    """
    Генерує випадкову карту печер у вигляді 3-регулярного графа (кожна печера має 'degree' суміжних печер)
    з використанням моделі парування
    """
    if num_caves * degree % 2 != 0:
        raise ValueError("Кількість печер * ступінь має бути парною")
    while True:
        stubs = []
        # Додаємо "стаби" для кожної печери
        for node in range(1, num_caves + 1):
            stubs.extend([node] * degree)
        random.shuffle(stubs)
        edges = []
        valid = True
        # робим пари та перевіряємо коректність з'єднань
        for i in range(0, len(stubs), 2):
            a = stubs[i]
            b = stubs[i + 1]
            if a == b or ((a, b) in edges or (b, a) in edges):
                valid = False
                break
            else:
                edges.append((a, b))
        if valid:
            break
    # словник печер та їх суміжностей
    caves = {node: [] for node in range(1, num_caves + 1)}
    for a, b in edges:
        caves[a].append(b)
        caves[b].append(a)
    return caves

class CaveMap:
    def __init__(self, num_caves=30, degree=3):
        # Ініціалізація карти печер
        self.caves = generate_cave_map(num_caves, degree)

    def get_neighbors(self, cave):
        # Повертає суміжні печери для заданої печери
        return self.caves.get(cave, [])

class Game:
    def __init__(self, num_caves=30):
        self.map = CaveMap(num_caves)
        self.player = random.choice(list(self.map.caves.keys()))
        # Вампус
        self.wumpus = random.choice([c for c in self.map.caves.keys() if c != self.player])
        # 3 пастки
        remaining = [c for c in self.map.caves.keys() if c not in (self.player, self.wumpus)]
        self.pits = random.sample(remaining, 3)
        # 2 печери з бетменами :)
        remaining = [c for c in remaining if c not in self.pits]
        self.bats = random.sample(remaining, 2)
        self.arrows = 5
        self.game_over = False

    def check_current_room(self):
        """
        Перевіряє поточну печеру на наявність небезпек
        Повертає відповідне повідомлення
        """
        if self.player == self.wumpus:
            self.game_over = True
            return "Ви увійшли в печеру Вампуса! Гра завершена."
        elif self.player in self.pits:
            self.game_over = True
            return "Ви впали в пастку! Гра завершена."
        elif self.player in self.bats:
            self.player = random.choice(list(self.map.caves.keys()))
            self.relocate_bats()
            return "Кажани перенесли вас в іншу печеру!"
        else:
            return self.get_hints()

    def get_hints(self):
        """
        Повертає підказки, якщо в суміжних печерах є небезпеки
        """
        neighbors = self.map.get_neighbors(self.player)
        hints = []
        if self.wumpus in neighbors:
            hints.append("відчуваєте запах Вампуса")
        if any(p in neighbors for p in self.pits):
            hints.append("відчуваєте холод пасток")
        if any(b in neighbors for b in self.bats):
            hints.append("чуєте шелест кажанів")
        return "; ".join(hints) if hints else "Немає небезпек поруч."

    def move_player(self, dest):
        # переміщуєм гравця, якщо обрана печера суміжна
        if dest in self.map.get_neighbors(self.player):
            self.player = dest
            return self.check_current_room()
        else:
            return "Ця печера не суміжна. Спробуйте ще раз."

    def shoot_arrow(self, path):
        """
        Симулює постріл стрілою за заданою послідовністю печер
        Якщо стріла потрапляє у Вампуса, гравець переможе
        """
        current = self.player
        for dest in path:
            if dest in self.map.get_neighbors(current):
                current = dest
                if current == self.wumpus:
                    self.game_over = True
                    return "Ваша стріла влучила у Вампуса! Ви виграли!"
            else:
                return f"Стріла не може пройти через печеру {dest}."
        self.arrows -= 1
        result = f"Стріла промахнулася. Залишилося стріл: {self.arrows}"
        if self.arrows == 0:
            self.game_over = True
            result += "\nВи використали всі стріли. Гра завершена."
        else:
            # 75% шанс, що Вампус переміститься після промаху
            if random.random() < 0.75:
                neighbors = self.map.get_neighbors(self.wumpus)
                if neighbors:
                    self.wumpus = random.choice(neighbors)
                    result += "\nВампус почув шум і перемістився!"
                    if self.wumpus == self.player:
                        self.game_over = True
                        result += "\nВампус увійшов у вашу печеру! Гра завершена."
        return result

    def relocate_bats(self):
        """
        Переміщує кажанів у нові печери, уникаючи позицій гравця, вампуса та пасток
        """
        available = [c for c in self.map.caves.keys() if c not in (self.player, self.wumpus) and c not in self.pits]
        if len(available) >= 2:
            self.bats = random.sample(available, 2)
        else:
            self.bats = available


class VisualGameApp:
    NODE_RADIUS = 20
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Hunt the Wumpus")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

        self.game = Game(num_caves=30)
        self.mode = "move"
        self.arrow_path = []
        self.node_positions = {}

        self.calculate_node_positions()

    def calculate_node_positions(self):
        # Обчислюємо позиції для кожної печери, розташовуючи їх по колу
        center_x = self.SCREEN_WIDTH // 2
        center_y = self.SCREEN_HEIGHT // 2
        radius = min(center_x, center_y) * 0.8
        num_nodes = len(self.game.map.caves)
        for i in range(1, num_nodes + 1):
            angle = 2 * math.pi * (i - 1) / num_nodes
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.node_positions[i] = (int(x), int(y))

    def draw_map(self):
        # Малюємо ребра між печерами
        drawn_edges = set()
        for node, neighbors in self.game.map.caves.items():
            x1, y1 = self.node_positions[node]
            for neighbor in neighbors:
                if (neighbor, node) in drawn_edges:
                    continue
                x2, y2 = self.node_positions[neighbor]
                pygame.draw.line(self.screen, (0, 0, 0), (x1, y1), (x2, y2), 2)
                drawn_edges.add((node, neighbor))
        # Малюємо самі печери (вузли)
        for node, (x, y) in self.node_positions.items():
            color = self.get_node_color(node)
            pygame.draw.circle(self.screen, color, (x, y), self.NODE_RADIUS)
            pygame.draw.circle(self.screen, (0, 0, 0), (x, y), self.NODE_RADIUS, 2)
            text = self.font.render(str(node), True, (0, 0, 0))
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)

    def get_node_color(self, node):
        # Якщо гра завершена, показуємо розташування небезпек
        if self.game.game_over:
            if node == self.game.wumpus:
                return (255, 0, 0)  # червоний для Вампуса
            if node in self.game.pits:
                return (128, 128, 128)  # сірий для пасток
            if node in self.game.bats:
                return (160, 32, 240)  # фіолетовий для кажанів
        # Виділяємо печеру гравця
        if node == self.game.player:
            return (0, 255, 0)  # зелений
        # У режимі переміщення підсвічуємо суміжні печери
        if self.mode == "move":
            if node in self.game.map.get_neighbors(self.game.player):
                return (173, 216, 230)  # світло-блакитний
        # У режимі стрільби підсвічуємо вибрані кроки
        if self.mode == "shoot":
            if node in self.arrow_path:
                return (255, 165, 0)  # помаранчевий
            if not self.arrow_path and node in self.game.map.get_neighbors(self.game.player):
                return (173, 216, 230)
            if self.arrow_path:
                last = self.arrow_path[-1]
                if node in self.game.map.get_neighbors(last):
                    return (173, 216, 230)
        return (255, 255, 255)  # білий

    def draw_status(self):
        # Відображаємо інформацію про гру: режим, позицію гравця, кількість стріл, шлях стрільби та підказки
        lines = [
            f"Режим: {self.mode}",
            f"Поточна печера: {self.game.player}",
            f"Стріл: {self.game.arrows}",
            f"Шлях стрільби: {self.arrow_path}",
            f"Підказки: {self.game.get_hints() if not self.game.game_over else ''}"
        ]
        y = 10
        for line in lines:
            text = self.font.render(line, True, (0, 0, 0))
            self.screen.blit(text, (10, y))
            y += 25
        if self.game.game_over:
            over_text = self.font.render("ГРА ЗАВЕРШЕНА. Натисніть R для перезапуску.", True, (255, 0, 0))
            self.screen.blit(over_text, (10, y))

    def get_node_at_pos(self, pos):
        # Повертає номер печери, якщо клік був по ній
        mx, my = pos
        for node, (x, y) in self.node_positions.items():
            if math.hypot(mx - x, my - y) <= self.NODE_RADIUS:
                return node
        return None

    def handle_mouse_click(self, pos):
        # Обробка кліку миші
        if self.game.game_over:
            return
        node = self.get_node_at_pos(pos)
        if not node:
            return
        if self.mode == "move":
            # У режимі переміщення переміщуємо гравця
            if node in self.game.map.get_neighbors(self.game.player):
                msg = self.game.move_player(node)
                print(msg)
                self.arrow_path = []  # очищення шляху стрільби
            else:
                print("Ця печера не суміжна.")
        elif self.mode == "shoot":
            # будуємо послідовність печер для стрільби
            if not self.arrow_path:
                if node in self.game.map.get_neighbors(self.game.player):
                    self.arrow_path.append(node)
                else:
                    print("Перший крок повинен бути суміжною печерою від вашої.")
            else:
                last = self.arrow_path[-1]
                if node in self.game.map.get_neighbors(last):
                    self.arrow_path.append(node)
                else:
                    print("Наступна печера має бути суміжною до останньої в шляху.")

    def handle_key(self, key):
        if key == pygame.K_m:
            self.mode = "move"
            self.arrow_path = []
        elif key == pygame.K_s:
            self.mode = "shoot"
            self.arrow_path = []
        elif key == pygame.K_SPACE:
            if self.mode == "shoot":
                result = self.game.shoot_arrow(self.arrow_path)
                print(result)
                self.arrow_path = []
        elif key == pygame.K_c:
            # Очистити шлях стрільби
            self.arrow_path = []
        elif key == pygame.K_r:
            self.game = Game(num_caves=30)
            self.mode = "move"
            self.arrow_path = []

    def run(self):
        running = True
        while running:
            self.clock.tick(30)  # 30 фпс
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(pygame.mouse.get_pos())
                if event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)

            self.screen.fill((240, 240, 240))
            self.draw_map()
            self.draw_status()
            pygame.display.flip()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = VisualGameApp()
    app.run()
