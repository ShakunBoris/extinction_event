import pgzero
import pgzrun # to run with play button
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


def helper_draw_enemy_paths():
    for npc in NPC.npcs:
        if  npc.hunter and npc.path and (npc.path != [] or npc.path != None):
            color = {'eric': 'green','dylan':'purple'}
            for cell in npc.path:
                r = Rect(cell[1] * TILE_SIZE, cell[0] * TILE_SIZE, TILE_SIZE-1, TILE_SIZE-1)
                if npc.name in color.keys():
                    screen.draw.rect(r, color[npc.name])        
                else:
                    screen.draw.rect(r, 'red')

def helper_draw_npc_sight():
    for npc in NPC.npcs:
        for cell in npc.sight:
            r = Rect(cell[0]+6, cell[1]+6, 4, 4)
            screen.draw.rect(r, 'yellow')
                   
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


class Game:
    def __init__(self):
        self.timer = 0
        self.time_limit = 120
        self._is_running = False     
        self.win_lose = 0
        self.blits = [] # objects are then loaded separately 
        
        self.xbox_price = BASE_XBOX_PRICE
        
        self._last_key_press = 0.0
        
        self.load_maze_blits_objects()  
        
        self.player = Player('pirate', hp=100,
                alive=True, 
                anchor=('left', 'top'), pos=(1 * TILE_SIZE, 1 * TILE_SIZE), 
                loot={'money': 50})
        
        self.eric = NPC('eric', alive=True, hunter=True, 
             anchor=('left', 'top'), pos=(16 * TILE_SIZE, 21 * TILE_SIZE))
        self.eric.weapon = Weapon('gun', 'gun', pos=self.eric.active_cell, anchor=('left', 'top'))
        self.dylan = NPC('dylan', alive=True, hunter=True, 
            anchor=('left', 'top'), pos=(16 * TILE_SIZE, 3 * TILE_SIZE))
        self.dylan.weapon = Weapon('gun', 'gun', pos=self.eric.active_cell, anchor=('left', 'top'))
        
        self.preys = []
        self.generate_preys(4)
        self.prey_spawn_timer = 0
        # self.test_npc = NPC('prey', alive=True, hunter=False, prey=True, hp=2000,
        #                         anchor=('left', 'top'), 
        #                         pos=(12 * TILE_SIZE, 21 * TILE_SIZE))
        # self.test_npc.weapon = None
        # self.preys.append(self.test_npc)
        
    def generate_preys(self, n_preys):
        for i in range(n_preys):
            row =  random.randint(5,15) 
            column =  random.randint(5,15) 
            if maze[row][column] != 1:
                npc = NPC('prey', alive=True, hunter=False, prey=True, hp=100,
                                anchor=('left', 'top'), 
                                pos=(column * TILE_SIZE, row * TILE_SIZE))
                npc.weapon = None
                if self.is_running:
                    npc.die()
                    npc.revive()
                self.preys.append(npc)
                
    def load_maze_blits_objects(self):
        for row in range(len(maze)):
            for column in range(len(maze[row])):
                x = column * TILE_SIZE
                y = row * TILE_SIZE
                tile = tiles[maze[row][column]]
                if tile in Object.images:
                    _ = Object(x,y,tile)
                else:
                    self.blits.append((tile, (x, y)))
    
    @property
    def is_running(self):
        return self._is_running

    @is_running.setter
    def is_running(self, value):
        if not isinstance(value, bool):
            raise ValueError("is_running must be a boolean")
        self._is_running = value

    def update(self, dt):
        
        self.xbox_price += self.xbox_price/100 * dt

        if keyboard.escape:
            exit()
            
        if self.is_running:
            
            self.player_control(dt)
                            
            global mouse_down_pos
            global MOUSE_CONTROL
            
            self.timer += dt
            
            # win condition
            if self.player.loot.items['money'] >= self.xbox_price:
                self.win_lose = 1
                self.is_running = False
            # lose condition
            elif self.timer >self.time_limit or \
                    self.player.hp <=0 or \
                        (self.eric.alive == False and \
                            self.dylan.alive==False and 
                            self.player.loot.items['money'] + 
                            self.eric.loot.items['money'] + 
                            self.dylan.loot.items['money'] < self.xbox_price):
                self.win_lose = -1
                self.is_running = False
            
            for npc in copy.copy(self.preys):
                if npc not in NPC.npcs:
                    self.preys.remove(npc)
            for npc in NPC.npcs:
                npc.update(dt)


            for bullet in Bullet.bullets:
                bullet.update(dt)
                
            if self.prey_spawn_timer > 5:
                self.prey_spawn_timer = 0
                self.generate_preys(1)
            self.prey_spawn_timer += dt            
                
            '''TELEPORT TO POINT'''
            if MOUSE_CONTROL == True :
                self.player.pos = (mouse_down_pos[0], mouse_down_pos[1])
                MOUSE_CONTROL = False
                        
            ''' for FF to pointer or next wall'''
            # if MOUSE_CONTROL == True and not self.player.collidepoint(mouse_down_pos):
            #     not_moved = 1
            #     if (mouse_down_pos[0] - self.player.x) > 0:
            #         not_moved *= self.player.move_mouse(self.player.x+TILE_SIZE, self.player.y)
            #     elif (mouse_down_pos[0] - self.player.x) < 0:
            #         not_moved *= self.player.move_mouse(self.player.x-TILE_SIZE, self.player.y)
            #     if (mouse_down_pos[1] - self.player.y) > 0:
            #         not_moved *= self.player.move_mouse(self.player.x, self.player.y + TILE_SIZE)
            #     elif (mouse_down_pos[1] - self.player.y) < 0:
            #         not_moved *= self.player.move_mouse(self.player.x, self.player.y - TILE_SIZE)
            #     if not_moved == 1:
            #         MOUSE_CONTROL = False
            # else:
            #     MOUSE_CONTROL = False
                

    def draw(self):
        screen.clear() 
        if self.is_running:
            screen.clear()   
            grid() 
            for b in self.blits:
                screen.blit(*b)
            for _ in Object.objects:
                screen.blit(_.image, (_.x, _.y)) # _.create()
            
            for bullet in Bullet.bullets:
                bullet.draw()
                
            self.eric.draw()
            self.player.draw()
            self.dylan.draw()
            for npc in self.preys:
                if npc.prey:
                    npc.draw()
            helper_draw_enemy_paths()
            helper_draw_npc_sight()
            

            self.draw_hps()
            self.draw_texts()
            
            draw_actor_aoe(self.player)
            
        if not self.is_running:
            self.draw_menu()

    
    def player_control(self, dt):
        
        self._last_key_press += dt
        
        if self._last_key_press <= 0.2:
            pass
        else: 
            row = int(self.player.y / TILE_SIZE)
            column = int(self.player.x / TILE_SIZE)   
            if keyboard.up:
                self._last_key_press = 0
                row = row - 1
            elif keyboard.down:
                self._last_key_press = 0
                row = row + 1
            elif keyboard.left:
                self._last_key_press = 0
                column = column - 1
            elif keyboard.right:
                self._last_key_press = 0
                column = column + 1
            new_x = column * TILE_SIZE
            new_y = row * TILE_SIZE
            self.player.move(new_x, new_y)
            
            if keyboard.z:
                self.player.hit()
                sounds.chop.play()
            elif keyboard.x:
                self.player.scream()
            # elif keyboard.f:
            #     self.test_npc.pos = (mouse_down_pos[0], mouse_down_pos[1])
    
    def draw_hps(self):
        for a in Actor.actors:
            screen.draw.text(f"hp:{a.hp:.0f}", 
                (a.x- TILE_SIZE, a.y+ TILE_SIZE), 
                color='red', fontsize=16, anchor=(0, 0)) 
            
    def draw_texts(self):
        screen.draw.text(f"Time Left: {self.time_limit - self.timer:.2f}", (320, 16), color='blue')   
        screen.draw.text(f"q = EXIT to MENU", (320, 32), color='blue')
        screen.draw.text(f'LOOT:', (320, 64), color='blue')
        line = 1
        for k, v in self.player.loot.items.items():
            screen.draw.text(f'{k}: {v}', (320, 64 + line*TILE_SIZE), color='white')
            line +=1
        screen.draw.text(f'XBOX price \n+ inflation: \n{self.xbox_price:.2f}', (320, 64 + line*TILE_SIZE), color='blue')
        line +=3
        screen.draw.text(f'Eric&Dylan loot:', (320, 64 + line*TILE_SIZE), color='White')
        line +=1
        d1 = self.eric.loot.items
        d2 = self.dylan.loot.items
        common_loot = {k: d1.get(k, 0) + d2.get(k, 0) for k in d1.keys() | d2.keys()}
        for k, v in common_loot.items():
            screen.draw.text(f'{k}: {v}', (320, 64 + line*TILE_SIZE), color='white')
            line +=1
        
    def draw_menu(self):

        
        screen.draw.text("1. Start game", (128, 256), color='green',  fontsize=32)
        screen.draw.text("2. Sound on/off", (128, 288), color='green',  fontsize=32)
        screen.draw.text("3. Exit", (128, 320), color='green',  fontsize=32)
        
        screen.draw.text('controls:\nq-menu\narrows-move around\nz-hit\nx-bring hunter\' attention', (0,0))
        screen.draw.text('''
                         collect money to buy xbox from corpses,
                         don"t stab other students,
                         bring eric and dylan attention 
                         to where students are''', (0,128))
        
        match self.win_lose:
            case 1:
                screen.draw.text(f'YOU WIN with \n {self.player.loot.items['money']}$', 
                                 (128, 192), color='red',  fontsize=64)
            case -1:
                screen.draw.text('YOU LOST', (128, 192), color='red',  fontsize=64)
            
    def __del__(self):
        pass

        # print('game.__del__: actors, players, npc, weapon, loot, objs clear \n \
        #     dont forget to USE WEAKREFS')
        
        
game = Game()



# Eric Harris and Dylan Klebold
# check_fix_spawn_pos()

music.play('soundtrack')

def draw():
    game.draw()

def update(dt):
    game.update(dt)

    
def on_mouse_down(pos):
    global MOUSE_CONTROL 
    MOUSE_CONTROL = True
    
    global mouse_down_pos 
    mouse_down_pos = (pos[0] - pos[0]%TILE_SIZE, pos[1]-pos[1]%TILE_SIZE)  

def on_key_down(key):
    global game
    if not game.is_running:
        match key:
            case keys.K_1:
                game.is_running = True
                if game.timer != 0:
                    Actor.actors.clear()
                    Player.players.clear()
                    NPC.npcs.clear()
                    Weapon.weapons.clear()
                    Bullet.bullets.clear()
                    Loot.all_loot.clear()
                    Object.objects.clear()
                    
                    game = Game()
                    game.is_running = True
                for n in NPC.npcs:
                    n.revive()
                return
            case keys.K_2:
                if music.is_playing('soundtrack'):
                    music.pause()
                else:
                    music.unpause()
            case keys.K_3:
                exit()
    else: 
        match key:
            case keys.Q:
                print(f'GAME PAUSED')
                # print('actors', Actor.actors)
                # print('objects', Object.objects)
                # print(len(Actor.actors))
                # print(len(Object.objects))
                # for n in NPC.npcs:
                #     print(f'{n.name} \n hunter: {n.hunter} \n prey:{n.prey}')
                    
                for npc in NPC.npcs:
                    npc.die()
                game.is_running = False

pgzrun.go() # self run