import os
import curses
import random
import time
from curses import wrapper
from curses.textpad import Textbox, rectangle
from perlin_noise import PerlinNoise

from player import Player
from hud import Window
from camera import Camera
from tile import Tile


def main(stdscr):
    stdscr.clear()
    curses.curs_set(False)

    f = open("logo.txt", "r")
    for i in range(8):
        stdscr.addstr(i + 5, 85, f.readline())
    f.close()

    curses.init_pair(100, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(101, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(102, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(103, curses.COLOR_WHITE, curses.COLOR_GREEN)

    def createButton1(color):
        rectangle(stdscr, 20, 97, 23, 114)
        stdscr.attroff(curses.color_pair(101))
        stdscr.addstr(21, 102, f"New Game")

    def createButton2(color):
        rectangle(stdscr, 24, 97, 27, 114)
        stdscr.attroff(curses.color_pair(101))
        stdscr.addstr(25, 101, f"Load Game")

    def createButton3(color):
        rectangle(stdscr, 32, 97, 35, 114)
        stdscr.attroff(curses.color_pair(101))
        stdscr.addstr(33, 104, f"Exit")

    select = 0

    def colorPick():
        if select == 0:
            stdscr.attron(curses.color_pair(101))
            createButton1(101)
            createButton2(100)
            createButton3(100)
        elif select == 1:
            createButton1(100)
            stdscr.attron(curses.color_pair(101))
            createButton2(101)
            createButton3(100)
        elif select == 2:
            createButton1(100)
            createButton2(100)
            stdscr.attron(curses.color_pair(101))
            createButton3(101)

    while True:
        try:
            stdscr.addstr(50, 165, f"Z = Select")
            stdscr.addstr(50, 180, f"X = Exit")
            colorPick()
            key = stdscr.getkey()
            if key == "KEY_UP":
                if select < 1:
                    select = 2
                    colorPick()
                    stdscr.refresh()
                else:
                    select -= 1
                    colorPick()
                    stdscr.refresh()
            elif key == "KEY_DOWN":
                if select > 1:
                    select = 0
                    colorPick()
                    stdscr.refresh()
                else:
                    select += 1
                    colorPick()
                    stdscr.refresh()
            elif key == "z" and select == 0:
                break

        except:
            pass
        stdscr.addstr(50, 165, f"Z = Select")
        stdscr.addstr(50, 180, f"X = Exit")
        stdscr.addstr(50, 50, f"Select: {select}")

    stdscr.clear()
    LOADING_LABEL = "Generating terrain..."
    stdscr.addstr(curses.LINES // 2, (curses.COLS // 2) - 9, LOADING_LABEL)
    stdscr.refresh()

    CAM_WIDTH = 161
    CAM_HEIGHT = 35
    GAME_X = 400 + 1
    GAME_Y = 400
    CAM_X = GAME_X // 2 - CAM_WIDTH // 2
    CAM_Y = GAME_Y // 2 - CAM_HEIGHT // 2

    cam = Camera(CAM_WIDTH, CAM_HEIGHT, CAM_X, CAM_Y)

    OCTAVE = 26  # random.randrange(25, 30)

    noise = PerlinNoise(octaves=OCTAVE, seed=random.randrange(0, 100000000))  # random.randrange(0, 100000)

    map = [[noise([i / (GAME_X * 0.2), j / (GAME_Y * 1.7)]) for j in range(GAME_X)] for i in range(GAME_Y)]

    # curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_YELLOW)
    # BLUE_AND_YELLOW = curses.color_pair(1)

    game_pad = curses.newpad(GAME_Y, GAME_X)
    # player_win = curses.newwin(CAM_HEIGHT, CAM_WIDTH, 1, 0)
    stdscr.refresh()
    curses.curs_set(False)

    map = [[noise([i / GAME_X, j / GAME_Y]) for j in range(GAME_X)] for i in range(GAME_Y)]

    for i in range(len(map)):
        for j in range(len(map[i])):
            if map[i][j] < -0.5:
                map[i][j] = [".", "b"]  # " "
            elif -0.5 <= map[i][j] < -0.4:
                map[i][j] = [".", "b"]  # .
            elif -0.4 <= map[i][j] < -0.3:
                map[i][j] = [" ", "b"]  # .
            elif -0.3 <= map[i][j] < -0.2:
                map[i][j] = [" ", "b"]  # -
            elif -0.2 <= map[i][j] < -0.1:
                map[i][j] = [" ", "b"]  # -
            elif -0.1 <= map[i][j] < 0:
                map[i][j] = [" ", "b"]  # =
            elif 0 <= map[i][j] < 0.1:
                map[i][j] = [".", "b"]  # +
            elif 0.1 <= map[i][j] < 0.2:
                map[i][j] = [":", "b"]  # *
            elif 0.2 <= map[i][j] < 0.3:
                map[i][j] = ["#", "b"]  # #
            elif 0.3 <= map[i][j] < 0.4:
                map[i][j] = [" ", "b"]  # %
            elif 0.4 <= map[i][j] < 0.5:
                map[i][j] = [" ", "b"]  # @
            elif map[i][j] > 0.5:
                map[i][j] = [" ", "b"]  # @

    os.system("")
    for i in range(len(map)):
        for j in range(len(map[i]) - 1):
            match map[i][j][0]:
                case ".":
                    game_pad.addstr(i, j, f"{map[i][j][0]}", curses.A_DIM)
                case ":":
                    game_pad.addstr(i, j, f"{map[i][j][0]}")
                case "#":
                    game_pad.addstr(i, j, f"{map[i][j][0]}", curses.A_PROTECT)
                case _:
                    game_pad.addstr(i, j, f"{map[i][j][0]}")

    stdscr.nodelay(True)

    # player setup
    p = Player(GAME_X // 2, GAME_Y // 2, 100, 100, 5, 10, game_pad, map)

    # inventory setup
    inv = Window("inv", 1, 162, 25, 46, "Inventory")
    # inv.create_window()

    # i = Inventory(162, 1, 46, 25)
    # i.create_inventory_window(stdscr)

    # stats setup
    # s = Stats(p, 162, 27, 46, 12)
    # s.create_stats_window(stdscr)
    stats = Window("stats", 26, 162, 11, 46, "Stats", p)
    # stats.create_window()

    # HLine under game window
    stdscr.hline(CAM_HEIGHT + 1, 75, 45, (CAM_WIDTH // 2) + 7)

    # info-menu setup
    infomenu = Window("info", 36, 0, 15, 75, "")
    # infomenu.create_window()

    # stdscr.addstr(40, 40, f"Floor: {p.floor}")

    # stdscr.addstr(42, 1, f"PX: {p.x}")
    # stdscr.addstr(42, 10, f"PY: {p.y}")

    stats.print_stats(p)

    while True:

        try:
            key = stdscr.getkey()
            if key == "KEY_LEFT":
                move_cam = p.move_left(map)
                if not p.can_left(map):
                    infomenu.print_info("You hit the wall!")
                # Debuging:
                else:
                    infomenu.print_info("You moved left.")
                # end
                if not p.x >= GAME_X - (CAM_WIDTH // 2) - 1 and CAM_X > 0 and move_cam:
                    CAM_X -= 1


            elif key == "KEY_RIGHT":
                move_cam = p.move_right(map, GAME_X)
                if not p.can_right(map, GAME_X):
                    infomenu.print_info(f"You hit the wall!")
                # Debuging:
                else:
                    infomenu.print_info(f"You moved right.")
                # end
                if p.x > CAM_WIDTH // 2 and move_cam and CAM_X <= GAME_X - CAM_WIDTH - 2:
                    CAM_X += 1


            elif key == "KEY_UP":
                move_cam = p.move_up(map)
                if not p.can_up(map):
                    infomenu.print_info(f"You hit the wall!")
                # Debuging:
                else:
                    infomenu.print_info(f"You moved up.")
                # end
                if not p.y >= GAME_Y - (CAM_HEIGHT // 2) - 1 and CAM_Y > 0 and move_cam:
                    CAM_Y -= 1


            elif key == "KEY_DOWN":
                move_cam = p.move_down(map, GAME_Y)
                if not p.can_down(map, GAME_Y):
                    infomenu.print_info(f"You hit the wall!")
                # Debuging:
                else:
                    infomenu.print_info(f"You moved down.")
                # end
                if p.y > CAM_HEIGHT // 2 and move_cam and CAM_Y <= GAME_Y - CAM_HEIGHT - 1:
                    CAM_Y += 1


            elif key == "q":
                curses.endwin()
                exit()
        except:
            pass

        game_pad.refresh(CAM_Y, CAM_X, 1, 1, CAM_HEIGHT, CAM_WIDTH)

        # Debuging:
        # stdscr.addstr(40, 1, f"X: {CAM_X}")
        # stdscr.addstr(40, 10, f"Y: {CAM_Y}")
        # stdscr.addstr(40, 20, f"Octave: {OCTAVE}")
        # stdscr.addstr(40, 40, f"Floor: {p.floor}")
        # stdscr.addstr(42, 1, f"PX: {p.x}")
        # stdscr.addstr(42, 10, f"PY: {p.y}")

        # rectangle(stdscr, 1, 162, 26, 208)
        # stdscr.addstr(1, 165, f" Inventory ")

        # rectangle(stdscr, 27, 162, 49, 208)
        # stdscr.addstr(27, 165, f" Stats ")

        # s.print_all()
        # s.update_stats(p)

        # stdscr.refresh()


if __name__ == '__main__':
    wrapper(main)
