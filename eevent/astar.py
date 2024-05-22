# Импортируем необходимые модули
import heapq  # Модуль для работы с очередью с приоритетами
import math   # Модуль для математических операций

# Определяем класс узла графа
class Node:
    def __init__(self, x, y):
        self.x = x  # Координата x узла на карте
        self.y = y  # Координата y узла на карте
        self.g = 0  # Расстояние от начального узла до текущего узла
        self.h = 0  # Примерное расстояние от текущего узла до конечного узла
        self.f = 0  # Сумма g и h
        self.parent = None  # Родительский узел, используется для восстановления пути

    # Переопределяем оператор сравнения для сравнения узлов
    def __lt__(self, other):
        return self.f < other.f

    # Переопределяем оператор равенства для сравнения узлов
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    # Переопределяем метод хеширования для использования в множествах и словарях
    def __hash__(self):
        return hash((self.x, self.y))

# Определяем функцию для нахождения пути с помощью алгоритма A*
def astar(start, end, obstacles):
    # Создаем начальный и конечный узлы
    start_node = Node(start[0], start[1])
    end_node = Node(end[0], end[1])

    # Инициализируем очередь с приоритетами
    open_list = []
    heapq.heappush(open_list, start_node)

    # Инициализируем множество посещенных узлов
    closed_set = set()

    # Пока очередь с приоритетами не пуста
    while open_list:
        # Извлекаем узел с наименьшей оценкой f
        current_node = heapq.heappop(open_list)

        # Если текущий узел является конечным
        if current_node == end_node:
            # Восстанавливаем путь от конечного узла до начального
            path = []
            while current_node is not None:
                path.append((current_node.x, current_node.y))
                current_node = current_node.parent
            return path[::-1]

        # Добавляем текущий узел в множество посещенных узлов
        closed_set.add(current_node)

        # Получаем соседние узлы
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Вверх, вниз, влево, вправо
        for dx, dy in directions:
            x = current_node.x + dx
            y = current_node.y + dy
            # Игнорируем узлы за пределами карты
            if x < 0 or x >= len(obstacles) or y < 0 or y >= len(obstacles[0]):
                continue
            # Игнорируем препятствия
            if obstacles[x][y] == 1:
                continue
            # Создаем новый узел и добавляем его в список соседей
            neighbor = Node(x, y)
            neighbors.append(neighbor)
        # for dx in range(-1, 2):
        #     for dy in range(-1, 2):
        #         # Игнорируем текущий узел
        #         if dx == 0 and dy == 0:
        #             continue

        #         # Вычисляем координаты соседнего узла
        #         x = current_node.x + dx
        #         y = current_node.y + dy
        #         # Игнорируем узлы за пределами карты
        #         if x < 0 or x >= len(obstacles) or y < 0 or y >= len(obstacles[0]):
        #             continue
                
        #         # Игнорируем препятствия
        #         if obstacles[x][y]:
        #             continue
        #         # Создаем новый узел и добавляем его в список соседей
        #         neighbor = Node(x, y)
        #         neighbors.append(neighbor)

        # Для каждого соседнего узла
        for neighbor in neighbors:
            # Если соседний узел уже был посещен, пропускаем его
            if neighbor in closed_set:
                continue

            # Вычисляем расстояние от начального узла до соседнего узла
            new_g = current_node.g + 1

            # Если соседний узел уже находится в очереди с приоритетами
            if nfo := next((n for n in open_list if n == neighbor), None):
                # Если новое расстояние до соседнего узла меньше, чем старое, обновляем значения g, h и f
                if new_g < nfo.g:
                    nfo.g = new_g
                    nfo.h = math.sqrt((end_node.x - nfo.x) ** 2 + (end_node.y - nfo.y) ** 2)
                    nfo.f = nfo.g + nfo.h
                    nfo.parent = current_node
                    # Обновляем приоритет соседнего узла в очереди с приоритетами
                    heapq.heapify(open_list)
            else:
                # Иначе добавляем соседний узел в очередь с приоритетами и вычисляем значения g, h и f
                neighbor.g = new_g
                neighbor.h = math.sqrt((end_node.x - neighbor.x) ** 2 + (end_node.y - neighbor.y) ** 2)
                neighbor.f = neighbor.g + neighbor.h
                neighbor.parent = current_node
                heapq.heappush(open_list, neighbor)

    # Если конечный узел недостижим, возвращаем None

    return None