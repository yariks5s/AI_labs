import random

def generate_cave_map(num_caves=30, degree=3):
    """
    Генерує випадковий 3-регулярний граф із заданою кількістю печер.
    Використовується метод парування (pairing model) із повторною генерацією у випадку помилки.
    """
    if num_caves * degree % 2 != 0:
        raise ValueError("Кількість печер * ступінь повинні давати парне число.")
    while True:
        stubs = []
        for node in range(1, num_caves + 1):
            stubs.extend([node] * degree)
        random.shuffle(stubs)
        edges = []
        valid = True
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
    caves = {node: [] for node in range(1, num_caves + 1)}
    for a, b in edges:
        caves[a].append(b)
        caves[b].append(a)
    return caves

class CaveMap:
    def __init__(self, num_caves=30, degree=3):
        self.caves = generate_cave_map(num_caves, degree)

    def get_neighbors(self, cave):
        return self.caves.get(cave, [])

class Game:
    def __init__(self, num_caves=30):
        self.map = CaveMap(num_caves)
        # Випадкова початкова позиція гравця
        self.player = random.choice(list(self.map.caves.keys()))
        #  Вампус (не на позиції гравця)
        self.wumpus = random.choice([c for c in self.map.caves.keys() if c != self.player])
        #  3 пасток
        remaining = [c for c in self.map.caves.keys() if c not in (self.player, self.wumpus)]
        self.pits = random.sample(remaining, 3)
        #  2 печер з кажанами
        remaining = [c for c in remaining if c not in self.pits]
        self.bats = random.sample(remaining, 2)
        self.arrows = 5
        self.game_over = False

    def display_status(self):
        print("\n-----------------------------")
        print(f"Ваша позиція: {self.player}")
        neighbors = self.map.get_neighbors(self.player)
        print("Суміжні печери:", neighbors)
        print(f"Кількість стріл: {self.arrows}")
        print("-----------------------------\n")

    def check_current_room(self):
        if self.player == self.wumpus:
            print("Ви потрапили у печеру з Вампусом! Гра завершена.")
            self.game_over = True
        elif self.player in self.pits:
            print("Ви впали у пастку! Гра завершена.")
            self.game_over = True
        elif self.player in self.bats:
            print("Кажани схопили вас і перенесли у випадкову печеру!")
            self.player = random.choice(list(self.map.caves.keys()))
            self.relocate_bats()
            self.check_current_room()
        else:
            self.display_hints()

    def display_hints(self):
        neighbors = self.map.get_neighbors(self.player)
        hints = []
        if self.wumpus in neighbors:
            hints.append("відчуваєте запах Вампуса")
        if any(p in neighbors for p in self.pits):
            hints.append("відчуваєте холод пасток")
        if any(b in neighbors for b in self.bats):
            hints.append("чуєте шурхіт крил кажанів")
        if hints:
            print("\nПідказки: " + "; ".join(hints))
        else:
            print("\nПоруч немає відчутних небезпек.")

    def move_player(self, dest):
        if dest in self.map.get_neighbors(self.player):
            self.player = dest
            self.check_current_room()
        else:
            print("Ця печера не суміжна з вашою. Спробуйте ще раз.")

    def shoot_arrow(self, path):
        current = self.player
        for dest in path:
            if dest in self.map.get_neighbors(current):
                current = dest
                if current == self.wumpus:
                    print("Стріла влучила у Вампуса! Ви перемогли!")
                    self.game_over = True
                    return True
            else:
                print("Стріла не може пройти через печеру", dest)
                break
        self.arrows -= 1
        print(f"Стріла не знайшла ціль. Залишилося стріл: {self.arrows}")
        if self.arrows == 0:
            print("Ви використали всі стріли. Гра завершена.")
            self.game_over = True
        else:
            # 75% шанс, що Вампус переміститься після промаху
            if random.random() < 0.75:
                neighbors = self.map.get_neighbors(self.wumpus)
                if neighbors:
                    self.wumpus = random.choice(neighbors)
                    print("Вампус почув шум і перемістився!")
                    if self.wumpus == self.player:
                        print("Вампус з'явився у вашій печері! Гра завершена.")
                        self.game_over = True
        return False

    def relocate_bats(self):
        # Переміщуємо кажанів у нові печери, не до граіця та пасток
        available = [c for c in self.map.caves.keys() if c not in (self.player, self.wumpus) and c not in self.pits]
        if len(available) >= 2:
            self.bats = random.sample(available, 2)
        else:
            self.bats = available

    def play(self):
        print("Ласкаво просимо до гри 'Світ Вампусу'!")
        while not self.game_over:
            self.display_status()
            command = input("Введіть команду (m - рух, s - стрільба, q - вихід): ").strip().lower()
            if command == 'm':
                try:
                    dest = int(input("Введіть номер суміжної печери: "))
                    self.move_player(dest)
                except ValueError:
                    print("Введіть, будь ласка, число.")
            elif command == 's':
                try:
                    path_input = input("Введіть послідовність печер через пробіл (наприклад: 12 5): ")
                    path = list(map(int, path_input.split()))
                    if self.shoot_arrow(path):
                        break
                except ValueError:
                    print("Некоректний ввід. Спробуйте ще раз.")
            elif command == 'q':
                print("Вихід з гри. До побачення!")
                break
            else:
                print("Невідома команда. Спробуйте ще раз.")
        print("Гра завершена.")

def main():
    game = Game(num_caves=30)
    game.play()

if __name__ == "__main__":
    main()
