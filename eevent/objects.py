import pgzero

from pgzero.actor import Actor as PGZActor
from .settings import *

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

# w = Weapon('saber', 'saber')

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