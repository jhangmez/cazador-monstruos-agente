# Contenido para src/memory/perception_action_table.py

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
from collections import Counter, defaultdict

@dataclass
class MemoryEntry:
    """
    Entrada en la tabla de memoria del agente.
    """
    timestamp: int
    position: Tuple[int, int, int]
    perception: Dict[str, Any]
    action_taken: str
    action_params: Dict[str, Any]
    success: bool

    def to_dict(self) -> Dict:
        """
        Convierte la entrada a diccionario.
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
    Tabla de mapeo percepción-acción para agentes con memoria interna.
    Ya no almacena un mapa de coordenadas, solo un historial de eventos.
    """

    def __init__(self):
        """
        Inicializa la tabla de memoria.
        """
        self.entries: List[MemoryEntry] = []
        self.position_history: List[Tuple[int, int, int]] = []
        self.monster_sightings: Dict[Tuple[int, int, int], int] = defaultdict(int)
        self.successful_actions: Counter = Counter()
        self.failed_actions: Counter = Counter()

    def add_entry(self, timestamp: int, position: Tuple[int, int, int],
                  perception: Dict[str, Any], action: str,
                  action_params: Dict[str, Any], success: bool):
        """
        Agrega una nueva entrada a la tabla de memoria.
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

        if perception.get('monster_detected', False):
            self.monster_sightings[position] += 1

        if success:
            self.successful_actions[action] += 1
        else:
            self.failed_actions[action] += 1

    def count_visits_to_position(self, position: Tuple[int, int, int]) -> int:
        """
        Cuenta cuántas veces el agente ha visitado una posición (solo para análisis).
        """
        return self.position_history.count(position)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de la memoria.
        """
        return {
            'total_entries': len(self.entries),
            'unique_positions': len(set(self.position_history)),
            'total_monster_sightings': sum(self.monster_sightings.values()),
            'successful_actions': dict(self.successful_actions),
            'failed_actions': dict(self.failed_actions)
        }

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convierte la tabla de memoria a DataFrame de pandas.
        """
        if not self.entries:
            return pd.DataFrame()

        data = [entry.to_dict() for entry in self.entries]
        return pd.DataFrame(data)