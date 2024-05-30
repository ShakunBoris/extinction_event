import pgzero

from pgzero.actor import Actor as PGZActor
from .settings import *
# from .actors import Actor

class Weapon(PGZActor):
    available_weapons = {
        'saber': {'damage': 10, 'shooting_speed': 1, 'bullet_speed': 0.1, 'range': 1},
        'gun': {'damage': 50, 'shooting_speed': 1, 'bullet_speed': 0.1, 'range': 10},
    }
    weapons = []
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if name in Weapon.available_weapons:
            self.name = name
            self.damage = Weapon.available_weapons[name]['damage']
            self.shooting_speed = Weapon.available_weapons[name]['shooting_speed']
            self.bullet_speed = Weapon.available_weapons[name]['bullet_speed']
            self.range = Weapon.available_weapons[name]['range']
            self.colliding = False
        else:
            raise ValueError(f"Weapon {name} is not available.")
        Weapon.weapons.append(self)
    
    def shoot(self, direction, pos):
        if self.name == 'gun':
            return Bullet('bullet', 
                          damage=self.damage, 
                          range=self.range, bullet_speed=self.bullet_speed, direction=direction, pos=pos)
        return None
    
class Bullet(PGZActor):
    bullets = []
    
    def __init__(self, image, damage, range, bullet_speed, direction, pos, *args, **kwargs):
        super().__init__(image,anchor=('left', 'top'), *args, **kwargs)
        self.damage = damage
        self.range = range
        self.bullet_speed =bullet_speed
        self.direction = direction
        self.pos = pos
        self.cells_passed = 0
        self._last_move=0
        Bullet.bullets.append(self)

    def update(self, dt):
        self.check_collision()
        self._last_move += dt
        if self._last_move >= self.bullet_speed:
            self.x += self.direction[0] 
            self.y += self.direction[1] 
            self.cells_passed += 1
            self._last_move = 0
            if self.cells_passed > self.range:
                self.__del__()
            self.check_collision()
        
    def check_collision(self):
        from .actors import Actor
        for actor in Actor.actors:
            if self.colliderect(actor) and actor.alive:
                actor._take_hit(None, self.damage)
                Bullet.bullets.remove(self)
                return
        
        if not (0 <= self.x <= WIDTH and 0 <= self.y <= HEIGHT):
            Bullet.bullets.remove(self)
    
    def draw(self):
        super().draw()
    
    def __del__(self):
        if self in Bullet.bullets:
            Bullet.bullets.remove(self)

class Loot:
    all_loot = []

    def __init__(self, x = 360, y = 360, items=None):
        if items is None or not isinstance(items, dict):
            items = {'money': random.randint(0,20)}  # По умолчанию, если items не задан

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
        global TILE_SIZE
        c = []
        for i in range(int(self.x), int(self.x+TILE_SIZE), 1):
            for j in range(int(self.y), int(self.y+TILE_SIZE), 1):
                c.append((i,j))
        return c
    
    # def create(self):
    #     screen.blit(self.image, (self.x, self.y))
        
        
    def __repr__(self) -> str:
        return f'\n{self.image}: ({self.x}, {self.y})'