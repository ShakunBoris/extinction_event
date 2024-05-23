import pgzero
import pgzrun # to run with play button
import eevent.astar as astar 
from eevent.settings import *
from eevent.actors import *
from eevent.objects import *



        
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

# Eric Harris and Dylan Klebold
pirate = Player('pirate', alive=True, anchor=('left', 'top'), pos=(1 * TILE_SIZE, 1 * TILE_SIZE))
eric = NPC('eric', alive=True, hunter=True, 
             anchor=('left', 'top'), pos=(2 * TILE_SIZE, 2 * TILE_SIZE))
dylan = NPC('dylan', alive=True, hunter=True, 
            anchor=('left', 'top'), pos=(6 * TILE_SIZE, 6 * TILE_SIZE))

music.play('soundtrack')
def draw():
    global GAME_ON
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
        screen.draw.text(str(pirate.loot), (0, 64), color='red')

        for w in Weapon.weapons:
            w.draw()
        for a in Actor.actors:
            screen.draw.text(f"hp:{a.hp:.0f}", 
                            (a.x- TILE_SIZE, a.y+ TILE_SIZE), 
                            color='red', fontsize=16, anchor=(0, 0))  
        screen.draw.text(f"Time passed: {TIMER:.2f}", (0, 0), color='red')   
        draw_actor_aoe(pirate)
        screen.draw.text(f"q = EXIT to MENU", (200, 0), color='red')
    
    if not GAME_ON:
        screen.draw.text("1. Start game", (128, 256), color='green',  fontsize=32)
        screen.draw.text("2. Sound on/off", (128, 288), color='green',  fontsize=32)
        screen.draw.text("3. Exit", (128, 320), color='green',  fontsize=32)
        
        screen.draw.text('controls:\nq-menu\narrows-move around\nz-hit\nx-bring hunter\' attention', (0,0))
        screen.draw.text('help eric and dylan to find their friends', (0,128))


def update(dt):
    global GAME_ON
    if keyboard.escape:
        exit()
        
    if GAME_ON:
        global mouse_down_pos
        global MOUSE_CONTROL
        global TIMER
        
        TIMER += dt
        
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


# HELPER.py
def grid():

    for i in range(0, HEIGHT, 16):
        screen.draw.line((0, i), (WIDTH, i), COLOR_GRAY)
        screen.draw.text(f'{i}', (0, i), color="black", fontsize=12, anchor=(0,0))
    for i in range(0, WIDTH, 16):
        screen.draw.line((i,0), (i,HEIGHT), COLOR_GRAY)
        screen.draw.text(f'{i}', (i, 0), color="black", fontsize=12, anchor=(0,0))

def helper_draw_enemy_paths():
    for npc in NPC.npcs:
        if npc.hunter and npc.path and npc.path != [] or npc.path != None:
            for cell in npc.path:
                r = Rect(cell[1] * TILE_SIZE, cell[0] * TILE_SIZE, TILE_SIZE-1, TILE_SIZE-1)
                screen.draw.rect(r, 'green')        
                
def draw_actor_aoe(actor):
    
    min_x = min(coord[0] for coord in actor.area_of_effect)
    min_y = min(coord[1] for coord in actor.area_of_effect)
    max_x = max(coord[0] for coord in actor.area_of_effect)
    max_y = max(coord[1] for coord in actor.area_of_effect)
    aoe_rect = Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    return screen.draw.rect(aoe_rect, 'red')

initial_collision_check = True
while initial_collision_check:
    initial_collision_check = False
    for a in Actor.actors:
        if a.alive:
            for o in Object.objects:
                if a.colliderect(o):
                    a.pos = (a.x+TILE_SIZE, a.y)
                    initial_collision_check = True
                    
# for a in Actor.actors:
#     clock.schedule_interval(a.cycle_animation, 0.1)
#     if a.hunter:
#         clock.schedule_interval(a.walk_path, 0.5)
# clock.schedule_interval(eric.cycle_animation, 0.1)
        
pgzrun.go() # self run