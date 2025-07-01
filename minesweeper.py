import random
import os
import sys
import tty
import termios
import time

class Minesweeper:
    def __init__(self, width=9, height=9, num_mines=10):
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.board = [[' ' for _ in range(width)] for _ in range(height)]
        self.mines = [[False for _ in range(width)] for _ in range(height)]
        self.revealed = [[False for _ in range(width)] for _ in range(height)]
        self.flags = [[False for _ in range(width)] for _ in range(height)]
        self.game_over = False
        self.cursor_x = 0
        self.cursor_y = 0
        self.start_time = None
        self.place_mines()

    def place_mines(self):
        mines_placed = 0
        while mines_placed < self.num_mines:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if not self.mines[y][x]:
                self.mines[y][x] = True
                mines_placed += 1

    def count_adjacent_mines(self, x, y):
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                new_y, new_x = y + dy, x + dx
                if (0 <= new_x < self.width and 
                    0 <= new_y < self.height and
                    self.mines[new_y][new_x]):
                    count += 1
        return count

    def reveal(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        if self.revealed[y][x] or self.flags[y][x]:
            # If the cell is already revealed and contains a number, check if we can auto-reveal around it
            if self.revealed[y][x] and self.board[y][x] != ' ':
                # Count adjacent flags
                adjacent_flags = 0
                safe_cells = []
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        new_y, new_x = y + dy, x + dx
                        if (0 <= new_x < self.width and 0 <= new_y < self.height):
                            if self.flags[new_y][new_x]:
                                adjacent_flags += 1
                            elif not self.revealed[new_y][new_x]:
                                safe_cells.append((new_x, new_y))
                
                # If the number matches the flag count, reveal all non-flagged adjacent cells
                if str(adjacent_flags) == self.board[y][x]:
                    for safe_x, safe_y in safe_cells:
                        self.reveal(safe_x, safe_y)
            return

        self.revealed[y][x] = True

        if self.mines[y][x]:
            self.game_over = True
            # Reveal all mines when game is over
            for my in range(self.height):
                for mx in range(self.width):
                    if self.mines[my][mx] and not self.revealed[my][mx]:
                        self.revealed[my][mx] = True
            return

        adjacent_mines = self.count_adjacent_mines(x, y)
        if adjacent_mines == 0:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    new_y, new_x = y + dy, x + dx
                    if (0 <= new_x < self.width and 0 <= new_y < self.height):
                        self.reveal(new_x, new_y)
        else:
            self.board[y][x] = str(adjacent_mines)

    def toggle_flag(self, x, y):
        if not self.revealed[y][x]:
            self.flags[y][x] = not self.flags[y][x]

    def check_win(self):
        for y in range(self.height):
            for x in range(self.width):
                if not self.mines[y][x] and not self.revealed[y][x]:
                    return False
        return True

    def display(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        # Display status bar
        remaining_mines = self.num_mines - sum(sum(row) for row in self.flags)
        elapsed_time = int(time.time() - self.start_time) if self.start_time else 0
        status_bar = f'💣 {remaining_mines:02d}'
        time_display = f'⏱️ {elapsed_time:03d}'
        padding = self.width * 3 - len(status_bar) - len(time_display)
        print(f'{status_bar}{" " * padding}{time_display}\n')
        # Display board
        for y in range(self.height):
            for x in range(self.width):
                cell = ' '
                if self.flags[y][x]:
                    cell = '\033[38;2;80;250;123m\033[0m'
                elif not self.revealed[y][x]:
                    cell = '\033[38;2;248;248;242m󰝤\033[0m'
                elif self.mines[y][x]:
                    cell = '\033[38;2;255;85;85m󰚑\033[0m'
                else:
                    cell = f'\033[38;2;98;114;164m{self.board[y][x]}\033[0m'
                
                # Add cursor indicator
                if x == self.cursor_x and y == self.cursor_y:
                    print(f'[{cell}]', end='')
                else:
                    print(f' {cell} ', end='')
            print()

def get_char():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def get_custom_config():
    while True:
        try:
            print("\nEnter board width (8-30): ")
            width = int(get_char())
            if not 8 <= width <= 30:
                print("Width must be between 8 and 30")
                continue

            print("\nEnter board height (8-30): ")
            height = int(get_char())
            if not 8 <= height <= 30:
                print("Height must be between 8 and 30")
                continue

            max_mines = (width * height) - 1
            print(f"\nEnter number of mines (1-{max_mines}): ")
            mines = int(get_char())
            if not 1 <= mines <= max_mines:
                print(f"Number of mines must be between 1 and {max_mines}")
                continue

            return width, height, mines
        except ValueError:
            print("Please enter valid numbers")

def main():
    print("Welcome to Minesweeper!")
    print("\nSelect difficulty:")
    print("1. Easy (9x9, 10 mines)")
    print("2. Medium (16x16, 40 mines)")
    print("3. Hard (16x30, 99 mines)")
    print("4. Custom")
    print("\nPress 1-4 to select: ")

    while True:
        choice = get_char()
        if choice == '1':
            game = Minesweeper(9, 9, 10)
            break
        elif choice == '2':
            game = Minesweeper(16, 16, 40)
            break
        elif choice == '3':
            game = Minesweeper(30, 16, 99)
            break
        elif choice == '4':
            width, height, mines = get_custom_config()
            game = Minesweeper(width, height, mines)
            break
        elif choice == 'q':
            print("\nGame quit by player")
            return
        else:
            print("\nInvalid choice. Press 1-4 to select: ")

    print("\nControls: h/j/k/l - move, r - reveal, f - flag, q - quit")
    print("Press any key to start...")
    get_char()
    game.start_time = time.time()

    while not game.game_over and not game.check_win():
        game.display()
        command = get_char()
        
        if command == 'h' and game.cursor_x > 0:
            game.cursor_x -= 1
        elif command == 'l' and game.cursor_x < game.width - 1:
            game.cursor_x += 1
        elif command == 'k' and game.cursor_y > 0:
            game.cursor_y -= 1
        elif command == 'j' and game.cursor_y < game.height - 1:
            game.cursor_y += 1
        elif command == 'r':
            game.reveal(game.cursor_x, game.cursor_y)
        elif command == 'f':
            game.toggle_flag(game.cursor_x, game.cursor_y)
        elif command == 'q':
            print("\nGame quit by player")
            return

    game.display()
    if game.game_over:
        print("\nGame Over! You hit a mine!")
    else:
        print("\nCongratulations! You won!")


if __name__ == "__main__":
    main()