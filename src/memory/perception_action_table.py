from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import pandas as pd
from collections import Counter, defaultdict


@dataclass
class MemoryEntry:
    """
    Entrada en la tabla de memoria del agente
    """
    timestamp: int
    position: Tuple[int, int, int]
    perception: Dict[str, Any]
    action_taken: str
    action_params: Dict[str, Any]
    success: bool

    def to_dict(self) -> Dict:
        """
        Convierte la entrada a diccionario
        """
        return {
            'timestamp': self.timestamp,
            'position': self.position,
            'perception': str(self.perception),
            'action': self.action_taken,
            'params': str(self.action_params),
            'success': self.success
        }


class PerceptionActionTable:
    """
    Tabla de mapeo percepción-acción para agentes con memoria interna
    """

    def __init__(self):
        """
        Inicializa la tabla de memoria
        """
        self.entries: List[MemoryEntry] = []
        self.position_history: List[Tuple[int, int, int]] = []
        self.void_map: set = set()
        self.monster_sightings: Dict[Tuple[int, int, int], int] = defaultdict(int)
        self.successful_actions: Counter = Counter()
        self.failed_actions: Counter = Counter()

    def add_entry(self, timestamp: int, position: Tuple[int, int, int],
                  perception: Dict[str, Any], action: str,
                  action_params: Dict[str, Any], success: bool):
        """
        Agrega una nueva entrada a la tabla de memoria
        """
        entry = MemoryEntry(
            timestamp=timestamp,
            position=position,
            perception=perception,
            action_taken=action,
            action_params=action_params,
            success=success
        )

        self.entries.append(entry)
        self.position_history.append(position)

        if perception.get('hit_void', False):
            attempted_pos = perception.get('attempted_position')
            if attempted_pos:
                self.void_map.add(attempted_pos)

        if perception.get('monster_detected', False):
            self.monster_sightings[position] += 1

        if success:
            self.successful_actions[action] += 1
        else:
            self.failed_actions[action] += 1

    def get_last_position(self) -> Optional[Tuple[int, int, int]]:
        """
        Obtiene la última posición registrada
        """
        if self.position_history:
            return self.position_history[-1]
        return None

    def is_position_void(self, position: Tuple[int, int, int]) -> bool:
        """
        Verifica si una posición es conocida como zona vacía
        """
        return position in self.void_map

    def get_monster_likelihood(self, position: Tuple[int, int, int]) -> int:
        """
        Obtiene la probabilidad de que haya un monstruo en una posición
        """
        return self.monster_sightings.get(position, 0)

    def get_action_success_rate(self, action: str) -> float:
        """
        Obtiene la tasa de éxito de una acción específica
        """
        successes = self.successful_actions.get(action, 0)
        failures = self.failed_actions.get(action, 0)
        total = successes + failures

        if total == 0:
            return 0.0
        return successes / total

    def has_been_at_position(self, position: Tuple[int, int, int]) -> bool:
        """
        Verifica si el agente ha estado en una posición
        """
        return position in self.position_history

    def count_visits_to_position(self, position: Tuple[int, int, int]) -> int:
        """
        Cuenta cuántas veces el agente ha visitado una posición
        """
        return self.position_history.count(position)

    def get_recent_perceptions(self, n: int = 10) -> List[MemoryEntry]:
        """
        Obtiene las n percepciones más recientes
        """
        return self.entries[-n:] if len(self.entries) >= n else self.entries

    def get_entries_by_action(self, action: str) -> List[MemoryEntry]:
        """
        Obtiene todas las entradas donde se ejecutó una acción específica
        """
        return [entry for entry in self.entries if entry.action_taken == action]

    def get_exploration_coverage(self, total_positions: int) -> float:
        """
        Calcula el porcentaje de exploración del espacio
        """
        unique_positions = len(set(self.position_history))
        return (unique_positions / total_positions) * 100 if total_positions > 0 else 0

    def analyze_patterns(self) -> Dict[str, Any]:
        """
        Analiza patrones en la memoria para extraer conocimiento
        """
        if not self.entries:
            return {}

        total_entries = len(self.entries)
        unique_positions = len(set(self.position_history))

        analysis = {
            'total_iterations': total_entries,
            'unique_positions_visited': unique_positions,
            'known_void_positions': len(self.void_map),
            'monster_sightings_count': sum(self.monster_sightings.values()),
            'most_visited_position': max(set(self.position_history),
                                        key=self.position_history.count) if self.position_history else None,
            'action_distribution': dict(self.successful_actions + self.failed_actions),
            'success_rates': {
                action: self.get_action_success_rate(action)
                for action in set(list(self.successful_actions.keys()) +
                                list(self.failed_actions.keys()))
            }
        }

        return analysis

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convierte la tabla de memoria a DataFrame de pandas
        """
        if not self.entries:
            return pd.DataFrame()

        data = [entry.to_dict() for entry in self.entries]
        return pd.DataFrame(data)

    def infer_safe_directions(self, current_position: Tuple[int, int, int]) -> List[str]:
        """
        Infiere direcciones seguras basándose en la memoria
        """
        safe_directions = []
        x, y, z = current_position

        directions = {
            'forward_x': (x + 1, y, z),
            'backward_x': (x - 1, y, z),
            'forward_y': (x, y + 1, z),
            'backward_y': (x, y - 1, z),
            'forward_z': (x, y, z + 1),
            'backward_z': (x, y, z - 1)
        }

        for direction, pos in directions.items():
            if pos not in self.void_map:
                safe_directions.append(direction)

        return safe_directions

    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de la memoria
        """
        return {
            'total_entries': len(self.entries),
            'unique_positions': len(set(self.position_history)),
            'void_positions_known': len(self.void_map),
            'total_monster_sightings': sum(self.monster_sightings.values()),
            'successful_actions': dict(self.successful_actions),
            'failed_actions': dict(self.failed_actions)
        }