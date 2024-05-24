import pgzero
import pgzrun # to run with play button
import eevent.astar as astar 
from eevent.settings import *
from eevent.actors import *
from eevent.objects import *

# HELPERS 
def grid():

    for i in range(0, HEIGHT, 16):
        screen.draw.line((0, i), (WIDTH, i), COLOR_GRAY)
        screen.draw.text(f'{i}', (0, i), color="black", fontsize=12, anchor=(0,0))
    for i in range(0, WIDTH, 16):
        screen.draw.line((i,0), (i,HEIGHT), COLOR_GRAY)
        screen.draw.text(f'{i}', (i, 0), color="black", fontsize=12, anchor=(0,0))

# # Генератор для циклического перебора цветов
# def color_cycle():
#     colors = ['green', 'red', 'blue', 'yellow', 'purple', 'orange']
#     while True:
#         for color in colors:
#             yield color

# # Создаем генератор
# color_generator = color_cycle()

def helper_draw_enemy_paths():
    for npc in NPC.npcs:
        if npc.hunter and npc.path and npc.path != [] or npc.path != None:
            # color = next(color_generator)
            color = {'eric': 'green','dylan':'purple'}
            for cell in npc.path:
                r = Rect(cell[1] * TILE_SIZE, cell[0] * TILE_SIZE, TILE_SIZE-1, TILE_SIZE-1)
                screen.draw.rect(r, color[npc.name])        
                
def draw_actor_aoe(actor):
    
    min_x = min(coord[0] for coord in actor.area_of_effect)
    min_y = min(coord[1] for coord in actor.area_of_effect)
    max_x = max(coord[0] for coord in actor.area_of_effect)
    max_y = max(coord[1] for coord in actor.area_of_effect)
    aoe_rect = Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    return screen.draw.rect(aoe_rect, 'red')

def check_fix_spawn_pos():
    initial_collision_check = True
    while initial_collision_check:
        initial_collision_check = False
        for a in Actor.actors:
            if a.alive:
                for o in Object.objects:
                    # if a.colliderect(o):
                    if a.pos == o.pos:
                        a.pos = (a.x+TILE_SIZE, a.y)
                        initial_collision_check = True


# class Game:
#     def __init__(self):
#         self._is_running = True
        
    
#     @property
#     def is_running(self):
#         return self._is_running

#     @is_running.setter
#     def is_running(self, value):
#         if not isinstance(value, bool):
#             raise ValueError("is_running must be a boolean")
#         self._is_running = value

#     def update(self):
#         if not self._is_running:
#             return
        
#         # Обработка логики игры
#         self.player_control()

#     def draw(self):
#         screen.clear()
#         screen.blit('background', (0, 0))  # Замените 'background' на имя вашего изображения фона
#         self.player.draw()

#     def player_control(self):
#         if keyboard.left:
#             self.player.x -= 5
#         if keyboard.right:
#             self.player.x += 5
#         if keyboard.up:
#             self.player.y -= 5
#         if keyboard.down:
#             self.player.y += 5

# game = Game()

# Loading maze to objects-walls and "blits"- boneless textures
blits = []
for row in range(len(maze)):
    for column in range(len(maze[row])):
        x = column * TILE_SIZE
        y = row * TILE_SIZE
        tile = tiles[maze[row][column]]
        if tile in Object.images:
            _ = Object(x,y,tile)
        else:
            blits.append((tile, (x, y)))

XBOX_PRICE = BASE_XBOX_PRICE
# Eric Harris and Dylan Klebold
pirate = Player('pirate', 
                alive=True, 
                anchor=('left', 'top'), pos=(1 * TILE_SIZE, 1 * TILE_SIZE), 
                loot={'money': 55})
eric = NPC('eric', alive=True, hunter=True, 
             anchor=('left', 'top'), pos=(1 * TILE_SIZE, 21 * TILE_SIZE))
dylan = NPC('dylan', alive=True, hunter=True, 
            anchor=('left', 'top'), pos=(16 * TILE_SIZE, 3 * TILE_SIZE))

check_fix_spawn_pos()

music.play('soundtrack')
def draw():
    global GAME_ON
    global XBOX_PRICE
    screen.clear() 
    if GAME_ON:
        screen.clear()   
        grid() 
        
        for b in blits:
            screen.blit(*b)
        for _ in Object.objects:
            screen.blit(_.image, (_.x, _.y)) # _.create()
        eric.draw()
        pirate.draw()
        dylan.draw()
        helper_draw_enemy_paths()
        # print(pirate.loot,)
        

        for w in Weapon.weapons:
            w.draw()
        for a in Actor.actors:
            screen.draw.text(f"hp:{a.hp:.0f}", 
                            (a.x- TILE_SIZE, a.y+ TILE_SIZE), 
                            color='red', fontsize=16, anchor=(0, 0))  
        screen.draw.text(f"Time passed: {TIMER:.2f}", (320, 16), color='blue')   
        draw_actor_aoe(pirate)
        screen.draw.text(f"q = EXIT to MENU", (320, 32), color='blue')
        
        screen.draw.text(f'LOOT:', (320, 64), color='blue')
        line = 1
        for k, v in pirate.loot.items.items():
            screen.draw.text(f'{k}: {v}', (320, 64 + line*TILE_SIZE), color='blue')
            line +=1
        screen.draw.text(f'XBOX price \n+ inflation: \n{XBOX_PRICE:.2f}', (320, 64 + line*TILE_SIZE), color='blue')
    
    if not GAME_ON:
        screen.draw.text("1. Start game", (128, 256), color='green',  fontsize=32)
        screen.draw.text("2. Sound on/off", (128, 288), color='green',  fontsize=32)
        screen.draw.text("3. Exit", (128, 320), color='green',  fontsize=32)
        
        screen.draw.text('controls:\nq-menu\narrows-move around\nz-hit\nx-bring hunter\' attention', (0,0))
        screen.draw.text('help eric and dylan to find their friends', (0,128))


def update(dt):
    global GAME_ON
    global XBOX_PRICE
    global TIMER
    
    XBOX_PRICE += XBOX_PRICE/100 * dt


    if keyboard.escape:
        exit()
        
    if GAME_ON:
        global mouse_down_pos
        global MOUSE_CONTROL
        
        TIMER += dt
        if pirate.loot.items['money'] >= XBOX_PRICE:
            GAME_ON = False
        # for npc in NPC.npcs:
        #     npc.update()
        
        if MOUSE_CONTROL == True and not pirate.collidepoint(mouse_down_pos):
            not_moved = 1
            if (mouse_down_pos[0] - pirate.x) > 0:
                not_moved *= pirate.move_mouse(pirate.x+TILE_SIZE, pirate.y)
            elif (mouse_down_pos[0] - pirate.x) < 0:
                not_moved *= pirate.move_mouse(pirate.x-TILE_SIZE, pirate.y)
            if (mouse_down_pos[1] - pirate.y) > 0:
                not_moved *= pirate.move_mouse(pirate.x, pirate.y + TILE_SIZE)
            elif (mouse_down_pos[1] - pirate.y) < 0:
                not_moved *= pirate.move_mouse(pirate.x, pirate.y - TILE_SIZE)
            if not_moved == 1:
                MOUSE_CONTROL = False
        else:
            MOUSE_CONTROL = False

    
def on_mouse_down(pos):
    global MOUSE_CONTROL 
    MOUSE_CONTROL = True
    
    global mouse_down_pos 
    mouse_down_pos = (pos[0] - pos[0]%TILE_SIZE, pos[1]-pos[1]%TILE_SIZE)  

def on_key_down(key):
    global GAME_ON
    if not GAME_ON:
        match key:
            case keys.K_1:
                GAME_ON = True
                for n in NPC.npcs:
                    clock.schedule_interval(n.walk_path, 0.5)
                return
            case keys.K_2:
                if music.is_playing('soundtrack'):
                    music.pause()
                else:
                    music.unpause()
            case keys.K_3:
                exit()
    row = int(pirate.y / TILE_SIZE)
    column = int(pirate.x / TILE_SIZE)
    if key == keys.Z:
        pirate.hit()   
    elif key == keys.UP:
        row = row - 1
    elif key == keys.DOWN:
        row = row + 1
    elif key == keys.LEFT:
        column = column - 1
    elif key == keys.RIGHT:
        column = column + 1
 
    elif key == keys.X:
        pirate.push()
    elif key == keys.Q:
        print(f'players: \n{Player.players},\n NPC: \n{NPC.npcs}')
        GAME_ON = False
        return
    new_x = column * TILE_SIZE
    new_y = row * TILE_SIZE
    pirate.move(new_x, new_y)



                    
        
pgzrun.go() # self run