import copy
import random
import pgzero
import pgzrun # to run with play button
from pgzero.actor import Actor as PGZActor
import pygame

import astar 


# + TODO CLASS OBJECT INHERIT FROM ACTOR (RENAME TO GAME_OBJECT)
# + TODO loot 
# TODO CALL THE GUYS
# TODO FINISH PUSH
# TODO REWORK SIGHT TO GAME_OBJECT. ACTION CELL
# TODO CUT AREA_OF_EFFECT ARRAY TO KEY POINTS: ACCORDING TO TILE_SIZES
# TODO NEW ABSTRACTION: PUT GAME INTO ONE CLASS 
# TODO NEW ABSTRACTION: CREATE LEVEL ABSTRACTION


# 512/8 = 64 // 512/16 = 32... 

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
for i in range(0, HEIGHT, TILE_SIZE):
        maze.append(random.choices([0,1], weights=[5, 1], k=int(WIDTH/TILE_SIZE)))
with open('original_maze.txt', 'w') as file:
    for line in maze:
        file.write(str(line)+ '\n')


class Weapon(PGZActor):
    available_weapons = {
        'saber': {'damage': 10, 'range': 1},
        'gun': {'damage': 15, 'range': 3},
    }
    weapons = []
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if name in Weapon.available_weapons:
            self.name = name
            self.damage = Weapon.available_weapons[name]['damage']
            self.range = Weapon.available_weapons[name]['range']
            self.colliding = False
        else:
            raise ValueError(f"Weapon {name} is not available.")
        Weapon.weapons.append(self)

w = Weapon('saber', 'saber')

class Loot:
    all_loot = []

    def __init__(self, x = 360, y = 360, items=None):
        if items is None or not isinstance(items, dict):
            items = {'money': 100}  # По умолчанию, если items не задан

        self.x = x
        self.y = y
        self.items = items
        Loot.all_loot.append(self)

    def add_items(self, new_items):
        for item, amount in new_items.items():
            if item in self.items:
                self.items[item] += amount
            else:
                self.items[item] = amount

    def remove_items(self, items_to_remove):
        for item, amount in items_to_remove.items():
            if item in self.items:
                self.items[item] -= amount
                if self.items[item] <= 0:
                    del self.items[item]

    def __repr__(self) -> str:
        # return 'STR __repr__'
        return f'Loot with items: {self.items}'
        
    def __str__(self) -> str:
        # return 'STR __str__'
        return f'{self.items}'
            
class Actor(PGZActor):
    actors = []
    states = {'stand': '_stand_', 
              'walk': '_walk_',
              'dead': '_dead_'}
    def __init__(self,  *args, 
                 aoe_distance = TILE_SIZE, 
  
                 alive:bool=False,
                 hp:int = 100,
                 anim_stand=None, 
                 **kwargs ): 
        super().__init__(*args, **kwargs)

        self.alive: bool = alive
        self.hp = hp
        
        self.loot = Loot(self.x, self.y)
        
        self.name = copy.copy(self._image_name)
        self.state = 'stand'
        self.active_animation = self._get_list_of_frames()
        self.animation_index = 0
        
        self.aoe_distance = aoe_distance
        self.direction = (self.x+TILE_SIZE, self.y)

        self.weapon = Weapon('saber', 'saber', pos=self.direction, anchor=('left', 'top'))
        
        self.path = []
        
        clock.schedule_interval(self.cycle_animation, 0.1)
        Actor.actors.append(self)
    
    def _get_list_of_frames(self):
        res = []
        counter = 1
        suffix = Actor.states[self.state]
        while True:
            tmp_str = self.name + suffix + str(counter)
            try:
                self.image = tmp_str
                res.append(tmp_str)
                counter+=1
            except Exception as e:
                # print(e, f'\ntotal frames for {self.name} in state {self.state} is \n {counter-1}') 
                return res
            
    def move(self, new_x, new_y):
        self._set_direction(new_x, new_y)
        if self._can_move_to(new_x, new_y):  
            if  0 <=new_x <= WIDTH - TILE_SIZE and 0 <=new_y <= HEIGHT - TILE_SIZE:    
                # animate(self, 
                #         duration=0.1, 
                #         pos = (new_x, new_y))
                self.pos = (new_x, new_y)
            else:
                if self._can_move_to(int(new_x % WIDTH),int( new_y % HEIGHT)):

                    self.x = int(new_x % WIDTH)
                    self.y = int(new_y % HEIGHT)
 
            self.pos = (int(self.x % WIDTH), int(self.y % HEIGHT))
            self.loot.x = new_x
            self.loot.y = new_y
            self._collect_loot(self.pos[0], self.pos[1])
            return 0


    def _collect_loot(self, new_x, new_y):
        for loot in Loot.all_loot:
            if loot != self.loot and new_x == loot.x and new_y == loot.y:
                self.loot.add_items(loot.items)
                Loot.all_loot.remove(loot)
                print(f'{self.name} collected {loot.items}')
                if self.loot.items['money'] == 300:
                    global GAME_ON
                    GAME_ON = False
    
    def _can_move_to(self, new_x, new_y):
        
        for obj in Object.objects:
            if (new_x, new_y) == obj.pos:
                return False
        
        for actor in Actor.actors:
            if not actor.alive and (new_x, new_y) == (actor.x, actor.y):
                return True
            if actor is not self and (new_x, new_y) == (actor.x, actor.y):
                return False
        
        return True
    
    def _set_direction(self, new_x, new_y):
        if new_x < self.x and self._can_move_to(new_x, new_y):# and new_x != self.weapon.x:
            self.direction = (self.x-2*TILE_SIZE, self.y)
            if hasattr(self, 'weapon'):
                self.weapon.anchor = ('right', 'top')
                self.weapon.angle = 90
        elif new_x < self.x and not self._can_move_to(new_x, new_y):       
            self.direction = (new_x, new_y)
            if hasattr(self, 'weapon'):
                self.weapon.anchor = ('right', 'top')
                self.weapon.angle = 90
        if new_x > self.x and self._can_move_to(new_x, new_y):# and new_x != self.weapon.x:
            self.direction = (self.x+2*TILE_SIZE, self.y)
            if hasattr(self, 'weapon'):
                self.weapon.anchor = ('left', 'bottom')
                self.weapon.angle = -90
        elif new_x > self.x and not self._can_move_to(new_x, new_y):  
            self.direction = (new_x, new_y)     
            if hasattr(self, 'weapon'):
                self.weapon.anchor = ('left', 'bottom')
                self.weapon.angle = -90
            
        if new_y < self.y and self._can_move_to(new_x, new_y):# and new_y != self.weapon.y:
            self.direction = (self.x, self.y-2*TILE_SIZE)
            if hasattr(self, 'weapon'):
                self.weapon.anchor = ('left', 'top')
                self.weapon.angle = 0
        elif  new_y < self.y and not self._can_move_to(new_x, new_y): 
            self.direction = (new_x, new_y)
            if hasattr(self, 'weapon'):
                self.weapon.anchor = ('left', 'top')
                self.weapon.angle = 0
        if new_y> self.y and self._can_move_to(new_x, new_y):# and new_y != self.weapon.y:
            self.direction = (self.x, self.y+2*TILE_SIZE)
            if hasattr(self, 'weapon'):
                self.weapon.anchor = ('right', 'bottom')
                self.weapon.angle = 180
        elif  new_y > self.y and not self._can_move_to(new_x, new_y): 
            self.direction = (new_x, new_y)
            if hasattr(self, 'weapon'):
                self.weapon.anchor = ('right', 'bottom')
                self.weapon.angle = 180
        if hasattr(self, 'weapon'):
            animate(self.weapon, duration=0.05, pos=(self.direction))
        # self.weapon.pos = self.direction
        
    
    def hit(self):
        test_damage = 50
        for actor in Actor.actors:
            if self.weapon.colliderect(actor) and actor != self:
                actor._take_hit(self, test_damage) # ADD WEAPON
    
    def _take_hit(self, damager, damage):
        if self.hp > 0:
            self.hp -= damage
        if self.hp <= 0:
            self.state = 'dead'
            self.alive = False
            self.active_animation=self._get_list_of_frames()

            
    def push(self):
        pass
    
    
    def cycle_animation(self):  
        if self.active_animation:
            self.animation_index = (self.animation_index + 1)% len(self.active_animation)
            self.image = self.active_animation[self.animation_index]
    
    @property
    def area_of_effect(self):
        aoe = []
        for i in range(int(self.x- self.aoe_distance), int(self.x+ 2* self.aoe_distance + 2), 1):
            for j in range(int(self.y- self.aoe_distance), int(self.y+ 2* self.aoe_distance + 2), 1):
                if  0<= i <= WIDTH and  0<=j<=HEIGHT:
                        aoe.append((i,j))
        return aoe

    def __repr__(self) -> str:
        return f'\n player:{self.name}: {self.pos} \n loot: \n {self.loot}'
    
    def __del__(self):
        if self in Actor.actors:
            Actor.actors.remove(self)
        # print(f'Actor {self} deleted')

class Player(Actor):
    players = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Player.players.append(self)
    
    def move_mouse(self, new_x, new_y):
        if self._can_move_to(new_x, new_y):  
            self.x = new_x
            self.y = new_y
            self.pos = (self.x % WIDTH, self.y % HEIGHT)
            return 0
        else:              
            return 1
    
    def __del__(self):
        if self in Player.players:
            Player.players.remove(self)
        super().__del__()
        # print(f'Player {self} deleted')
        
        
class NPC(Actor):
    npcs = []
    def __init__(self, *args, hunter:bool=False, prey:bool=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.hunter: bool = hunter
        self.prey: bool = prey
        self.search_target = None
        clock.schedule_interval(self.walk_path, 0.5)
        NPC.npcs.append(self)
        
    def _calculate_new_path_to(self, destination):
        global maze
        start = (int(self.y // TILE_SIZE), int(self.x // TILE_SIZE))
        end = (int(destination[1] // TILE_SIZE), int(destination[0] // TILE_SIZE))
        maze_object_actors = copy.deepcopy(maze)
        for a in Actor.actors:
            row, column = int(a.y//TILE_SIZE),  int(a.x//TILE_SIZE)
            maze_object_actors[row][column] = 1
        self.path = astar.astar(start, end, maze_object_actors)
        
    def revive(self):
        self.alive = True
        self.state = 'stand'
        self._get_list_of_frames()
        self.loot = Loot(self.x, self.y)
        clock.schedule_interval(self.walk_path, 0.5)
        
    def walk_path(self):
        if self.alive == False:
            clock.unschedule(self.walk_path)
            clock.schedule(self.revive, 5)
            return
        if self.path == [] or self.path == None:
            if not self.search_target:
                x = random.randint(0, 31) * TILE_SIZE
                y = random.randint(0, 31) * TILE_SIZE
            else:
                x = random.randint(0, 31) * TILE_SIZE # ALL TEMP NO CHECK FOR SEARCH TARGET
                y = random.randint(0, 31) * TILE_SIZE
            self._calculate_new_path_to((x, y))
        elif self.path != None:
            # path maze inverted to path coords
            if self._can_move_to(self.path[0][1]*TILE_SIZE, self.path[0][0]*TILE_SIZE):
                self.move(self.path[0][1]*TILE_SIZE, self.path[0][0]*TILE_SIZE)
                self.path.pop(0)
            else:
                self._calculate_new_path_to((self.path[-1][1]*TILE_SIZE, self.path[-1][0]*TILE_SIZE))
                
    def __del__(self):
        if self in NPC.npcs:
            NPC.npcs.remove(self)
        super().__del__()
        # print(f'NPC {self} deleted')

class Object(PGZActor):
    images = ['wall']
    objects = []
    def __init__(self, x, y, image:str) -> None:
        super().__init__(image)
        self.x = int(x)
        self.y = int(y)
        self.pos = (x, y)
        if image in Object.images:
            self.image = image
        else:
            raise Exception(f'NO SUCH IMAGE: {image} \n FOUND IN OBJECT CLASS: {Object.images}')
        
        self.collision = []
        self.collision = self.__calculate_collision()
        Object.objects.append(self)
    
    def __calculate_collision(self):
        c = []
        for i in range(int(self.x), int(self.x+TILE_SIZE), 1):
            for j in range(int(self.y), int(self.y+TILE_SIZE), 1):
                c.append((i,j))
        return c
    
    def create(self):
        screen.blit(self.image, (self.x, self.y))
        
    def __repr__(self) -> str:
        return f'\n{self.image}: ({self.x}, {self.y})'

# Eric Harris and Dylan Klebold
pirate = Player('pirate', alive=True, anchor=('left', 'top'), pos=(1 * TILE_SIZE, 1 * TILE_SIZE))
eric = NPC('eric', alive=True, hunter=True, 
             anchor=('left', 'top'), pos=(2 * TILE_SIZE, 2 * TILE_SIZE))
dylan = NPC('dylan', alive=True, hunter=True, 
            anchor=('left', 'top'), pos=(6 * TILE_SIZE, 6 * TILE_SIZE))


mouse_down_pos = (pirate.x, pirate.y)


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
            # screen.blit(tile, (x, y))

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
            _.create()
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
    # mouse_down_pos = (pos[0], pos[1])

def on_key_down(key):
    global GAME_ON
    if not GAME_ON:
        match key:
            case keys.K_1:
                GAME_ON = True
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