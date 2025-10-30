import curses
import random
import time

# --- Curses 颜色常量 ---
# 定义颜色对的常量
COLOR_UNREVEALED = 1
COLOR_FLAG = 2
COLOR_MINE = 3
COLOR_NUMBER = 4
COLOR_CURSOR = 5
COLOR_STATUS = 6
COLOR_BG = 7

ICON_FLAG = ""
ICON_UNREVEALED = ""
ICON_MINE = "*"

class Minesweeper:

    # x轴字符倍率 3x:1y
    x_multiple = 3

    def __init__(self, stdscr, width=9, height=9, num_mines=10):
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.num_flag = num_mines
        self.num_revealed = 0

        self.board = [[' ' for _ in range(width)] for _ in range(height)]
        self.mines = [[False for _ in range(width)] for _ in range(height)]
        self.revealed = [[False for _ in range(width)] for _ in range(height)]
        self.flags = [[False for _ in range(width)] for _ in range(height)]
        self.game_over = False
        self.cursor_x = 0
        self.cursor_y = 0
        self.start_time = int(time.time())
        # 顶部偏移量
        self.top_offset = 1
        # 左侧偏移量
        self.left_offset = 3
        self.place_mines()
        self.stdscr = stdscr
        self.init_color()
        self.stdscr.clear()
        self.draw_border()
        self.draw_game()

    def init_color(self):
        # 1. 未揭开的单元格 (黑字白底)
        curses.init_pair(COLOR_UNREVEALED, curses.COLOR_BLACK, curses.COLOR_WHITE)
        # 2. 旗帜 (绿色)
        # curses.init_color(COLOR_FLAG, 314, 980, 482)
        curses.init_pair(COLOR_FLAG, curses.COLOR_GREEN, curses.COLOR_BLACK)
        # 3. 地雷 (白字红底)
        curses.init_pair(COLOR_MINE, curses.COLOR_WHITE, curses.COLOR_RED)
        # 4. 数字 (青色/蓝色)
        curses.init_pair(COLOR_NUMBER, curses.COLOR_CYAN, curses.COLOR_BLACK)
        # 5. 游标 (黑字黄底，用于反转显示)
        curses.init_pair(COLOR_CURSOR, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        # 6. 状态栏 (白字黑底)
        # curses.init_pair(COLOR_STATUS, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(COLOR_STATUS, curses.COLOR_BLACK, curses.COLOR_WHITE)

        curses.init_pair(COLOR_BG, -1, -1)
        self.stdscr.bkgd(' ', curses.color_pair(COLOR_BG))

    def get_icon(self):
        cur_icon = ICON_UNREVEALED
        if self.flags[self.cursor_y][self.cursor_x]:
            cur_icon = ICON_FLAG
        elif self.revealed[self.cursor_y][self.cursor_x]:
            cur_icon = self.board[self.cursor_y][self.cursor_x]
        return cur_icon

    def get_color(self, x, y):
        color = COLOR_UNREVEALED
        if self.flags[y][x]:
            color = COLOR_FLAG
        elif self.revealed[y][x]:
            color = COLOR_NUMBER
        return color


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
            if self.revealed[y][x] and self.board[y][x] != ' ':
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

                if str(adjacent_flags) == self.board[y][x]:
                    for safe_x, safe_y in safe_cells:
                        self.reveal(safe_x, safe_y)
            return

        self.revealed[y][x] = True

        if self.mines[y][x]:
            self.game_over = True
            self.draw_status(' GameOver ')
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
        self.num_revealed += 1
        self.game_over = self.check_win()

    def draw_status(self, status):
        self.stdscr.addstr(self.height + self.top_offset, (self.width * self.x_multiple) // 2 - 2, status, curses.color_pair(COLOR_STATUS) | curses.A_BOLD)

    def toggle_flag(self, x, y):
        if not self.revealed[y][x]:
            if self.flags[y][x]:
                self.num_flag += 1
            else:
                self.num_flag -= 1
            self.flags[y][x] = not self.flags[y][x]
            self.stdscr.addstr(self.cursor_y + self.top_offset, self.cursor_x * self.x_multiple + self.left_offset, f'[{self.get_icon()}]',  curses.color_pair(self.get_color(x, y)))
            self.refresh_mine()

    def check_win(self):
        return self.num_revealed == self.height * self.width - self.num_mines

    def draw_game(self):
        """使用 curses 绘制游戏板和状态栏"""
        # --- 绘制游戏板 ---
        # 从第一行开始绘制 (y=1)
        for y in range(self.height):
            for x in range(self.width):
                # 定义单元格内容和颜色/属性
                content = ' '
                attr = curses.A_NORMAL

                if self.flags[y][x]:
                    content = ICON_FLAG
                    attr = curses.color_pair(COLOR_FLAG) | curses.A_BOLD
                elif not self.revealed[y][x]:
                    content = ICON_UNREVEALED
                    attr = curses.color_pair(COLOR_UNREVEALED)
                elif self.mines[y][x]:
                    content = ICON_MINE
                    attr = curses.color_pair(COLOR_MINE) | curses.A_BOLD
                else:
                    content = self.board[y][x]
                    # 数字颜色
                    attr = curses.color_pair(COLOR_NUMBER)
                # 如果是游标所在位置，则应用反色属性 (突出显示)
                if x == self.cursor_x and y == self.cursor_y:
                    content = f'[{content}]'
                else:
                    content = f' {content} '
                # y 偏移 1 (避开状态栏和空行)，x 偏移 1
                self.stdscr.addstr(y + self.top_offset, x * self.x_multiple + self.left_offset, content, attr)

    def refresh_time(self):
        if not self.game_over:
            elapsed_time = int(time.time() - (self.start_time if self.start_time is not None else time.time()))
            status_bar = f'{elapsed_time:03d}'
            self.stdscr.addstr(0, (self.width * self.x_multiple) // 2 + 11, status_bar, curses.color_pair(COLOR_STATUS) | curses.A_BOLD)

    def refresh_mine(self):
        if (self.check_win()):
            self.num_flag = 0
        status_bar = f'{self.num_flag:02d}'
        self.stdscr.addstr(0, (self.width * self.x_multiple) // 2, status_bar, curses.color_pair(COLOR_STATUS) | curses.A_BOLD)

    def draw_border(self):
        # --- 绘制状态栏 ---
        status_bar = f' MINE: {self.num_flag:02d} | TIME: 000 '
        top_border = f' ┏{"━" * (self.width * self.x_multiple + self.left_offset - 1) }┓ '
        bottom_border = f' ┗{"━" * (self.width * self.x_multiple + self.left_offset - 1) }┛ '
        # 绘制状态栏在第一行
        self.stdscr.addstr(0, 0, top_border, curses.color_pair(COLOR_STATUS) | curses.A_BOLD)
        self.stdscr.addstr(0, (self.width * self.x_multiple) // 2 - 7, status_bar, curses.color_pair(COLOR_STATUS) | curses.A_BOLD)
        for y in range(self.height):
            self.stdscr.addstr(y + self.top_offset, 0, " ┃ ", curses.color_pair(COLOR_STATUS) | curses.A_BOLD)
            self.stdscr.addstr(y + self.top_offset, self.width * self.x_multiple + self.left_offset, " ┃ ", curses.color_pair(COLOR_STATUS) | curses.A_BOLD)
        self.stdscr.addstr(self.height + self.top_offset, 0, bottom_border, curses.color_pair(COLOR_STATUS) | curses.A_BOLD)

    def left_move(self):
        self.stdscr.addstr(self.cursor_y + self.top_offset, self.cursor_x * self.x_multiple + self.left_offset, f' {self.get_icon()} ', curses.color_pair(self.get_color(self.cursor_x, self.cursor_y)))
        self.cursor_x = (self.cursor_x - 1) % self.width
        self.stdscr.addstr(self.cursor_y + self.top_offset, self.cursor_x * self.x_multiple + self.left_offset, f'[{self.get_icon()}]', curses.color_pair(self.get_color(self.cursor_x, self.cursor_y)))

    def right_move(self):
        self.stdscr.addstr(self.cursor_y + self.top_offset, self.cursor_x * self.x_multiple + self.left_offset, f' {self.get_icon()} ', curses.color_pair(self.get_color(self.cursor_x, self.cursor_y)))
        self.cursor_x = (self.cursor_x + 1) % self.width
        self.stdscr.addstr(self.cursor_y + self.top_offset, self.cursor_x * self.x_multiple + self.left_offset, f'[{self.get_icon()}]', curses.color_pair(self.get_color(self.cursor_x, self.cursor_y)))

    def up_move(self):
        self.stdscr.addstr(self.cursor_y + self.top_offset, self.cursor_x * self.x_multiple + self.left_offset, f' {self.get_icon()} ', curses.color_pair(self.get_color(self.cursor_x, self.cursor_y)))
        self.cursor_y = (self.cursor_y - 1) % self.height
        self.stdscr.addstr(self.cursor_y + self.top_offset, self.cursor_x * self.x_multiple + self.left_offset, f'[{self.get_icon()}]', curses.color_pair(self.get_color(self.cursor_x, self.cursor_y)))

    def down_move(self):
        self.stdscr.addstr(self.cursor_y + self.top_offset, self.cursor_x * self.x_multiple + self.left_offset, f' {self.get_icon()} ', curses.color_pair(self.get_color(self.cursor_x, self.cursor_y)))
        self.cursor_y = (self.cursor_y + 1) % self.height
        self.stdscr.addstr(self.cursor_y + self.top_offset, self.cursor_x * self.x_multiple + self.left_offset, f'[{self.get_icon()}]', curses.color_pair(self.get_color(self.cursor_x, self.cursor_y)))

def main(stdscr):

    curses.start_color()
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(300)
    try:
        curses.use_default_colors()
    except curses.error:
        pass

    stdscr.addstr(0, 1, "Welcome to Minesweeper!")
    stdscr.addstr(1, 1, "Select difficulty:")
    stdscr.addstr(2, 1, "1. Easy (9x9, 10 mines)")
    stdscr.addstr(3, 1, "2. Medium (16x16, 40 mines)")
    stdscr.addstr(4, 1, "3. Hard (16x30, 99 mines)")
    stdscr.addstr(6, 1, "Press 1-3 to select: ")

    width = 0
    height = 0
    num_mines = 0

    while True:
        key = stdscr.getch()
        if key == -1:
            continue
        if key == ord('q'):
            return
        elif key == 49:
            height = 9
            width = 9
            num_mines = 10
            break
        elif key == 50:
            height = 16
            width = 16
            num_mines = 40
            break
        elif key == 51:
            height = 16
            width = 30
            num_mines = 99
            break

    game = Minesweeper(stdscr, width, height, num_mines)

    while True:
        key = stdscr.getch()
        # 更新计时器
        game.refresh_time()
        if key == -1:
            continue

        if not game.game_over:
            if key == ord('h'):
                game.left_move()
            elif key == ord('l'):
                game.right_move()
            elif key == ord('k'):
                game.up_move()
            elif key == ord('j'):
                game.down_move()
            elif key == ord('r'):
                game.reveal(game.cursor_x, game.cursor_y)
                game.draw_game()
            elif key == ord('f'):
                game.toggle_flag(game.cursor_x, game.cursor_y)
        else:
            if key == ord('r'):
                game = Minesweeper(stdscr, width, height, num_mines)

        if game.check_win():
            game.draw_status(" YouWin ")

        if key == ord('q'):
            return

if __name__ == "__main__":
    curses.wrapper(main)
