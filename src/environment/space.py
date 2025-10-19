import numpy as np
from enum import Enum
from typing import Tuple, List, Optional, Set
from dataclasses import dataclass

class CellType(Enum):
    """
    Tipos de celdas en el entorno 3D
    """
    FREE = 0
    VOID = 1
    ROBOT = 2
    MONSTER = 3
    DESTROYED = 4


@dataclass
class Position:
    """
    Representa una posición en el espacio 3D
    """
    x: int
    y: int
    z: int

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    def to_tuple(self) -> Tuple[int, int, int]:
        """
        Convierte la posición a tupla
        """
        return (self.x, self.y, self.z)

    def is_valid(self, n: int) -> bool:
        """
        Verifica si la posición es válida dentro de los límites del espacio
        """
        return 0 <= self.x < n and 0 <= self.y < n and 0 <= self.z < n

    def distance_to(self, other: 'Position') -> float:
        """
        Calcula la distancia euclidiana a otra posición
        """
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)

    def manhattan_distance_to(self, other: 'Position') -> int:
        """
        Calcula la distancia Manhattan a otra posición
        """
        return abs(self.x - other.x) + abs(self.y - other.y) + abs(self.z - other.z)


class Direction(Enum):
    """
    Direcciones en el espacio 3D
    """
    FORWARD_X = (1, 0, 0)
    BACKWARD_X = (-1, 0, 0)
    FORWARD_Y = (0, 1, 0)
    BACKWARD_Y = (0, -1, 0)
    FORWARD_Z = (0, 0, 1)
    BACKWARD_Z = (0, 0, -1)

    def get_offset(self) -> Tuple[int, int, int]:
        """
        Obtiene el offset de la dirección
        """
        return self.value


class OperationalSpace:
    """
    Representa el entorno de operación 3D
    """

    def __init__(self, n: int, p_free: float, random_state: Optional[np.random.RandomState] = None):
        """
        Inicializa el espacio operacional
        """
        self.n = n
        self.p_free = p_free
        self.random_state = random_state if random_state else np.random.RandomState()

        self.grid = np.zeros((n, n, n), dtype=int)
        self.robot_positions: Set[Position] = set()
        self.monster_positions: Set[Position] = set()
        self.void_positions: Set[Position] = set()

        self._initialize_space()

    def _initialize_space(self):
        """
        Inicializa el espacio con zonas libres y vacías de forma aleatoria
        """
        total_cells = self.n ** 3
        n_free = int(total_cells * self.p_free)

        flat_indices = self.random_state.permutation(total_cells)
        free_indices = flat_indices[:n_free]
        void_indices = flat_indices[n_free:]

        for idx in free_indices:
            x = idx // (self.n * self.n)
            y = (idx % (self.n * self.n)) // self.n
            z = idx % self.n
            self.grid[x, y, z] = CellType.FREE.value

        for idx in void_indices:
            x = idx // (self.n * self.n)
            y = (idx % (self.n * self.n)) // self.n
            z = idx % self.n
            self.grid[x, y, z] = CellType.VOID.value
            self.void_positions.add(Position(x, y, z))

    def get_cell_type(self, position: Position) -> CellType:
        """
        Obtiene el tipo de celda en una posición
        """
        if not position.is_valid(self.n):
            return CellType.VOID
        return CellType(self.grid[position.x, position.y, position.z])

    def is_free(self, position: Position) -> bool:
        """
        Verifica si una posición está libre
        """
        if not position.is_valid(self.n):
            return False
        cell_type = self.get_cell_type(position)
        return cell_type == CellType.FREE

    def is_void(self, position: Position) -> bool:
        """
        Verifica si una posición es una zona vacía
        """
        if not position.is_valid(self.n):
            return True
        return self.get_cell_type(position) == CellType.VOID

    def set_robot(self, position: Position):
        """
        Coloca un robot en una posición
        """
        if self.is_free(position):
            self.grid[position.x, position.y, position.z] = CellType.ROBOT.value
            self.robot_positions.add(position)

    def set_monster(self, position: Position):
        """
        Coloca un monstruo en una posición
        """
        if self.is_free(position):
            self.grid[position.x, position.y, position.z] = CellType.MONSTER.value
            self.monster_positions.add(position)

    def remove_robot(self, position: Position):
        """
        Elimina un robot de una posición
        """
        if position in self.robot_positions:
            self.grid[position.x, position.y, position.z] = CellType.FREE.value
            self.robot_positions.discard(position)

    def remove_monster(self, position: Position):
        """
        Elimina un monstruo de una posición
        """
        if position in self.monster_positions:
            self.grid[position.x, position.y, position.z] = CellType.FREE.value
            self.monster_positions.discard(position)

    def destroy_cell(self, position: Position):
        """
        Destruye una celda convirtiéndola en zona vacía
        """
        if position.is_valid(self.n):
            self.grid[position.x, position.y, position.z] = CellType.VOID.value
            self.void_positions.add(position)
            self.robot_positions.discard(position)
            self.monster_positions.discard(position)

    def move_entity(self, from_pos: Position, to_pos: Position, entity_type: CellType):
        """
        Mueve una entidad de una posición a otra
        """
        if not to_pos.is_valid(self.n) or self.is_void(to_pos):
            return False

        if entity_type == CellType.ROBOT:
            self.remove_robot(from_pos)
            self.set_robot(to_pos)
        elif entity_type == CellType.MONSTER:
            self.remove_monster(from_pos)
            self.set_monster(to_pos)

        return True

    def get_adjacent_positions(self, position: Position) -> List[Position]:
        """
        Obtiene las posiciones adyacentes a una posición dada (6 caras del cubo)
        """
        adjacent = []
        for direction in Direction:
            dx, dy, dz = direction.get_offset()
            new_pos = Position(position.x + dx, position.y + dy, position.z + dz)
            if new_pos.is_valid(self.n):
                adjacent.append(new_pos)
        return adjacent

    def get_free_positions(self) -> List[Position]:
        """
        Obtiene todas las posiciones libres en el espacio
        """
        free_positions = []
        for x in range(self.n):
            for y in range(self.n):
                for z in range(self.n):
                    pos = Position(x, y, z)
                    if self.is_free(pos):
                        free_positions.append(pos)
        return free_positions

    def get_random_free_position(self) -> Optional[Position]:
        """
        Obtiene una posición libre aleatoria
        """
        free_positions = self.get_free_positions()
        if not free_positions:
            return None
        return self.random_state.choice(free_positions)

    def count_entities(self) -> dict:
        """
        Cuenta las entidades en el espacio
        """
        return {
            'robots': len(self.robot_positions),
            'monsters': len(self.monster_positions),
            'void': len(self.void_positions),
            'free': np.sum(self.grid == CellType.FREE.value)
        }