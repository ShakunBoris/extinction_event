import pgzero
import pgzrun
import ast
from eevent.settings import *


class Brush:
    def __init__(self):
        self.current = 0  # 0 - пол, 1 - стены

    def set_brush(self, value):
        self.current = value

brush = Brush()
mouse_down = False

def load_maze():
    if os.path.exists(MAZE_FILE):
        with open(MAZE_FILE) as file:
            tmp_list = []
            for line in file:
                tmp_list.append(ast.literal_eval(line))
                # tmp_list.append(list(map(int, line.strip().strip('][').split(', '))))
            return tmp_list
    else:
        return [[0 for _ in range(int(WIDTH//TILE_SIZE))] for _ in range(int(HEIGHT//TILE_SIZE))]



def save_maze():
    with open(MAZE_FILE, 'w') as file:
        for row in tmp_maze:
            file.write(str(row) + '\n')
            
def grid():
    for i in range(0, HEIGHT, TILE_SIZE):
        screen.draw.line((0, i), (WIDTH, i), 'black')
        screen.draw.text(f'{i}', (0, i), color="black",
                         fontsize=12, anchor=(0, 0))
    for i in range(0, WIDTH, TILE_SIZE):
        screen.draw.line((i, 0), (i, HEIGHT), 'black')
        screen.draw.text(f'{i}', (i, 0), color="black",
                         fontsize=12, anchor=(0, 0))

tmp_maze = load_maze()

mouse_pos = (0, 0)
def draw():
    global tmp_maze
    screen.clear()
    screen.fill('grey')

    # Рисуем пол и стены
    for y in range(int(HEIGHT//TILE_SIZE)):
        for x in range(int(WIDTH//TILE_SIZE)):
            if tmp_maze[y][x] == 0:
                screen.blit('empty', (x * TILE_SIZE, y * TILE_SIZE))
            elif tmp_maze[y][x] == 1:
                Actor('wall', (x * TILE_SIZE, y * TILE_SIZE),
                      anchor=('left', 'top')).draw()

    grid()
    screen.draw.text(f'Mouse: {mouse_pos}, ({int(mouse_pos[0]/16)}, {int(mouse_pos[1]/16)})', (256, 16), color='red', alpha=0.5)
    
    screen.draw.text('1-empty floor', (16, 16), color='red', alpha=0.5)
    screen.draw.text('2-wall', (16, 32), color='red', alpha=0.5)
    screen.draw.text('\'s\'- SAVE MAP maze_lvl_0.txt',
                     (16, 48), color='red', alpha=0.5)


def on_key_down(key):
    if key == keys.K_1:
        brush.set_brush(0)
    elif key == keys.K_2:
        brush.set_brush(1)
    elif key == keys.S:
        save_maze()


def on_mouse_down(pos):
    global mouse_down
    mouse_down = True
    update_maze(pos)

def on_mouse_up(pos):
    global mouse_down
    mouse_down = False

def on_mouse_move(pos):
    global mouse_pos
    mouse_pos = (pos[0] - pos[0] % TILE_SIZE, pos[1] - pos[1] % TILE_SIZE)
    if mouse_down:
        update_maze(pos)

def update_maze(pos):
    x, y = pos
    grid_x = x // TILE_SIZE
    grid_y = y // TILE_SIZE
    if 0 <= grid_x < 32 and 0 <= grid_y < 32:
        tmp_maze[grid_y][grid_x] = brush.current


def update():
    pass


pgzrun.go()  # запуск Pygame Zero
