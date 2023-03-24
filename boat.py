from random import randint, choice


class Dot:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass

class WrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, dot_start, direction, length):
        self.dot_start = dot_start
        self.direction = direction
        self.length = length
        self.left_length = length

    @property
    def set_dots(self):
        dots = []
        for i in range(self.left_length):
            set_x = self.dot_start.x
            set_y = self.dot_start.y
            if self.direction == 'x':
                dots.append(Dot(set_x + i, set_y))
            elif self.direction == 'y':
                dots.append(Dot(set_x, set_y + i))
        return dots

    def hit(self, shot):
        return shot in self.set_dots


class Board:
    def __init__(self, show=True, size=6):
        self.show = show
        self.size = size
        self.count = 0
        self.field = [['■' for _ in range(size)] for _ in range(size)]
        self.busy = []
        self.ships = []

    def __str__(self):
        res = "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if not self.show:
            res = res.replace("0", "■")
            res = res.replace("K", "■")
        return res

    def in_board(self, dot):
        return 0 <= dot.x < self.size and 0 <= dot.y < self.size

    def contour(self, ship, kill=False):
        near_dots = [(-1, -1), (-1, 0), (-1, 1),
                     (0, -1), (0, 0), (0, 1),
                     (1, -1), (1, 0), (1, 1)]
        for dot in ship.set_dots:
            for dot_x, dot_y in near_dots:
                contour_dot = Dot(dot_x + dot.x, dot_y + dot.y)
                if self.in_board(contour_dot) and contour_dot not in self.busy:
                    if kill:
                        self.field[contour_dot.x][contour_dot.y] = '.'
                        self.field[dot.x][dot.y] = 'x'
                self.busy.append(contour_dot)

    def add_ship(self, ship):
        for dot in ship.set_dots:
            if (not self.in_board(dot)) or (dot in self.busy):
                raise WrongShipException()
        for dot in ship.set_dots:
            self.field[dot.x][dot.y] = 'K'
            self.busy.append(dot)
        self.ships.append(ship)
        self.contour(ship)

    def shot(self, dot):
            if dot in self.busy:
                print('Эта клетка уже занята. Выстрелите в другую клетку.')
                return True
            for ship in self.ships:
                if ship.hit(dot):
                    ship.length -= 1
                    self.busy.append(dot)
                    self.field[dot.x][dot.y] = 'x'
                    if ship.length == 0:
                        print('Корабль уничтожен!')
                        self.count += 1
                        ship.length = ship.left_length
                        self.contour(ship, kill=True)
                        return True
                    else:
                        print('Попадание! Возможность сделать еще один ход.')
                        return True
            self.field[dot.x][dot.y] = '.'
            print('Мимо!')
            self.busy.append(dot)
            return False

    def set_game(self):
        self.busy = []


class Player:
    def __init__(self, own, enemy):
        self.own = own
        self.enemy = enemy

    def ask_move(self):
        pass

    def move(self):
        while True:
            try:
                target = self.ask_move()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException:
                print(BoardException)


class User(Player):
    def ask_move(self):
        while True:
            coordinates = input("Пожалуйста, введите код вашего хода: ").split()
            if len(coordinates) != 2:
                print('Пожалуйста, укажите 2 числа - координаты хода.')
                continue
            x, y = coordinates
            if not x.isdigit() or not y.isdigit():
                print('Пожалуйста, введите числа.')
                continue
            x = int(x)
            y = int(y)
            if x not in range(1, self.own.size) or y not in range(1, self.own.size):
                print('Вводите цифры в диапазоне от 1 до 6!')
                continue
            return Dot(x - 1, y - 1)


class AI(Player):
    def ask_move(self):
        x, y = randint(0, 5), randint(0, 5)
        print(f'Ход компьютера: {x + 1} {y + 1}')
        return Dot(x, y)


class Game:
    def __init__(self, size=6):
        self.size = size
        player = self.random_board()
        ai = self.random_board()
        ai.show = False
        self.player = User(player, ai)
        self.ai = AI(ai, player)

    def random_board(self):
        board = None
        while board is None:
            board = self.set_board()
        return board

    def set_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for life in lens:
            while True:
                attempts += 1
                if attempts > 1000:
                    return None
                ship = Ship(Dot(randint(0, self.size - 1), randint(0, self.size - 1)), choice(['x', 'y']), life)
                try:
                    board.add_ship(ship)
                    break
                except WrongShipException:
                    pass
        board.set_game()
        return board

    def hello(self):
        print('''Приветствуем Вас в игре 'Морской бой'. Правила игры:
         В эту игру Вы играете против искусственного интеллекта, который совершает ходы случайно. Размерность поля - 
         6х6, число кораблей и их размеры: 4 однопалубных корабля, 2 двухпалубных корабля и 1 трехпалубный корабль.
         Ваша задача - совершая ходы, уничтожить все корабли оппонента.
         Правила выполнения ходов: вводите в качестве хода 2 цифры через пробел, 1 цифра - номер линии по горизонтали,
         2 цифра - номер линии по вертикали.''')

    def play(self):
        moves = 0
        while True:
            print('-' * 20)
            print('Ваша доска:')
            print(self.player.own)
            print('Доска ИИ:')
            print(self.ai.own)
            if moves % 2 == 0:
                print("-" * 20)
                print("Ход пользователя.")
                repeat = self.player.move()
            if moves % 2 == 1:
                print("-" * 20)
                print("Ход компьютера.")
                repeat = self.ai.move()
            if repeat:
                moves -= 1
            moves += 1
            if self.ai.own.count == len(self.ai.own.ships):
                print("-" * 20)
                print("Поздравлям, Вы победили!")
                break
            if self.player.own.count == len(self.player.own.ships):
                print("-" * 20)
                print("Компьютер победил. Не отчаивайтесь, попробуйте ещё!")
                break

    def start_game(self):
        self.hello()
        self.play()


game = Game()
game.start_game()
