import  random as rnd
class T:
    def __init__(self, name) -> None:
        self.name = name
        
a = T('a')
b = T('b')
print(__package__)
# class Actor:
#     actors = []
    
#     def __init__(self) -> None:
#         self.actor_name = 'Abobo'
#         Actor.actors.append(self)
#     def __repr__(self) -> str:
#         return self.actor_name
    
#     def destroy(self):
#         Actor.actors.remove(self)
    
# class NPC(Actor):
#     npcs = []
    
#     def __init__(self) -> None:
#         super().__init__()
#         self.npc_name = 'Nbobo'
#         NPC.npcs.append(self)
    
#     def __repr__(self) -> str:
#         return self.npc_name
    
#     def destroy(self):
#         super().destroy()
#         NPC.npcs.remove(self)
    
# # Создание и удаление NPC
# n = NPC()
# print('npcs:', NPC.npcs)  # Убедитесь, что NPC добавлен
# print('actors:', Actor.actors)  # Убедитесь, что Actor добавлен

# # Удаление NPC
# n.destroy()
# print('npcs:', NPC.npcs) # Убедитесь, что NPC удален
# print('actors:', Actor.actors)  # Убедитесь, что Actor удален