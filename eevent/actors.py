import pgzero
from pgzero.clock import clock
from pgzero.actor import Actor as PGZActor
from .objects import *
from .settings import *
from .astar import astar
import copy


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
                 loot = dict | None,
                 **kwargs ): 
        super().__init__(*args, **kwargs)

        self.alive: bool = alive
        self.hp = hp
        
        self.loot = Loot(self.x, self.y, loot)
        
        self.name = copy.copy(self._image_name)
        self.state = 'stand'
        self.active_animation = self._get_list_of_frames()
        self.animation_index = 0
        
        self.aoe_distance = aoe_distance
        self.active_cell = (self.x+TILE_SIZE, self.y)

        self.weapon = Weapon('saber', 'saber', pos=self.active_cell, anchor=('left', 'top'))
        
        self.path = []
        
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
            self.active_cell = (self.x-2*TILE_SIZE, self.y)
            if hasattr(self, 'weapon'):
                self.weapon.anchor = ('right', 'top')
                self.weapon.angle = 90
        elif new_x < self.x and not self._can_move_to(new_x, new_y):       
            self.active_cell = (new_x, new_y)
            if hasattr(self, 'weapon'):
                self.weapon.anchor = ('right', 'top')
                self.weapon.angle = 90
        if new_x > self.x and self._can_move_to(new_x, new_y):# and new_x != self.weapon.x:
            self.active_cell = (self.x+2*TILE_SIZE, self.y)
            if hasattr(self, 'weapon'):
                self.weapon.anchor = ('left', 'bottom')
                self.weapon.angle = -90
        elif new_x > self.x and not self._can_move_to(new_x, new_y):  
            self.active_cell = (new_x, new_y)     
            if hasattr(self, 'weapon'):
                self.weapon.anchor = ('left', 'bottom')
                self.weapon.angle = -90
            
        if new_y < self.y and self._can_move_to(new_x, new_y):# and new_y != self.weapon.y:
            self.active_cell = (self.x, self.y-2*TILE_SIZE)
            if hasattr(self, 'weapon'):
                self.weapon.anchor = ('left', 'top')
                self.weapon.angle = 0
        elif  new_y < self.y and not self._can_move_to(new_x, new_y): 
            self.active_cell = (new_x, new_y)
            if hasattr(self, 'weapon'):
                self.weapon.anchor = ('left', 'top')
                self.weapon.angle = 0
        if new_y> self.y and self._can_move_to(new_x, new_y):# and new_y != self.weapon.y:
            self.active_cell = (self.x, self.y+2*TILE_SIZE)
            if hasattr(self, 'weapon'):
                self.weapon.anchor = ('right', 'bottom')
                self.weapon.angle = 180
        elif  new_y > self.y and not self._can_move_to(new_x, new_y): 
            self.active_cell = (new_x, new_y)
            if hasattr(self, 'weapon'):
                self.weapon.anchor = ('right', 'bottom')
                self.weapon.angle = 180
        if hasattr(self, 'weapon'):
            self.weapon.pos = self.active_cell


        
    
    def hit(self):
        test_damage = 50
        for actor in Actor.actors:
            if self.weapon.colliderect(actor) and actor != self:
                actor._take_hit(self, test_damage) # ADD WEAPON
    
    def _take_hit(self, damager, damage):
        if self.hp > 0:
            self.hp -= damage
        if self.hp <= 0:
            self.die()

            
    def scream(self):
        for npc in NPC.npcs:
            npc.hear_scream(self.pos)

    
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
        NPC.npcs.append(self)
        
    def _calculate_new_path_to(self, destination):
        global maze
        start = (int(self.y // TILE_SIZE), int(self.x // TILE_SIZE))
        end = (int(destination[1] // TILE_SIZE), int(destination[0] // TILE_SIZE))
        maze_object_actors = copy.deepcopy(maze)
        for a in Actor.actors:
            row, column = int(a.y//TILE_SIZE),  int(a.x//TILE_SIZE)
            if end != (row, column):
                maze_object_actors[row][column] = 1
        self.path = astar(start, end, maze_object_actors)
        
    def revive(self):
        self.alive = True
        self.state = 'stand'
        self.active_animation = self._get_list_of_frames()
        clock.schedule_interval(self.cycle_animation, 0.1)
        clock.schedule_interval(self.walk_path, 0.5)
    
    def die(self):
        self.state = 'dead'
        self.alive = False
        self.active_animation = self._get_list_of_frames()
        clock.unschedule(self.cycle_animation)
        clock.unschedule(self.walk_path)
        
    def walk_path(self):
        if self.alive == False:
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
                if len(self.path) == 1 and self.search_target != None:
                    self.search_target = None
                    self.path = None
                    
            else:
                self._calculate_new_path_to((self.path[-1][1]*TILE_SIZE, self.path[-1][0]*TILE_SIZE))
    
    def hear_scream(self, pos):
        if self.hunter and self.search_target != pos:
            self.search_target = pos
            self._calculate_new_path_to((int(self.search_target[0]), int(self.search_target[1])))

            
            
            
    def __del__(self):
        if self in NPC.npcs:
            NPC.npcs.remove(self)
        super().__del__()
        # print(f'NPC {self} deleted')