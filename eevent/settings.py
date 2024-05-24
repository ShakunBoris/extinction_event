import random
import os
import ast
# from .objects import *


TILE_SIZE = 16
WIDTH = TILE_SIZE * 32
HEIGHT = TILE_SIZE * 32

COLOR_GRAY = (128, 128, 128)

TIMER = 0

MOUSE_CONTROL = False
DEBUG_COUNTER = 0

GAME_ON = False

tiles = ['empty', 'wall']
maze = []
MAZE_FILE = 'maze_lvl_0.txt'
if os.path.exists(MAZE_FILE):
    with open(MAZE_FILE) as file:
        for line in file:
            maze.append(ast.literal_eval(line))
            # maze.append(list(map(int, line.strip().strip('][').split(', '))))
else:
    for i in range(0, HEIGHT, TILE_SIZE):
        maze.append(random.choices([0, 1], weights=[
                    5, 1], k=int(WIDTH/TILE_SIZE)))
