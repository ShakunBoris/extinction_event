l1 = [(1,2), (1,3), (1,4)]
l2 = [(1,2), (2,3), (2,4)]
print(set(l1).intersection(l2))
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