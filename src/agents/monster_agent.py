from typing import Dict, Any, Tuple, List
import numpy as np
from dataclasses import dataclass

from .base_agent import BaseAgent, AgentState, Perception, Action


class MonsterState(AgentState):
    """
    Estado interno del monstruo (agente reflejo simple)
    """
    
    def __init__(self, agent_id: str, initial_position: Tuple[int, int, int]):
        super().__init__(agent_id)
        self.position = initial_position
        self.movements_made = 0
        self.last_movement_iteration = 0
    
    def update(self, perception: Perception, action: Action):
        """
        Actualiza el estado del monstruo
        """
        if action.action_type == 'move' and action.success:
            self.position = action.parameters.get('new_position', self.position)
            self.movements_made += 1
            self.last_movement_iteration = perception.timestamp


class MonsterAgent(BaseAgent):
    """
    Agente monstruo (reflejo simple) que se mueve aleatoriamente
    """
    
    def __init__(self, agent_id: str, initial_position: Tuple[int, int, int],
                 movement_frequency: int = 3, movement_probability: float = 0.4,
                 random_state: np.random.RandomState = None):
        """
        Inicializa el agente monstruo
        """
        self.initial_position = initial_position
        self.movement_frequency = movement_frequency
        self.movement_probability = movement_probability
        self.random_state = random_state if random_state else np.random.RandomState()
        super().__init__(agent_id)
    
    def _initialize_state(self) -> MonsterState:
        """
        Inicializa el estado del monstruo
        """
        return MonsterState(self.agent_id, self.initial_position)
    
    def should_attempt_movement(self, current_iteration: int) -> bool:
        """
        Determina si el monstruo debe intentar moverse en esta iteración
        """
        if current_iteration % self.movement_frequency != 0:
            return False
        
        return self.random_state.random() < self.movement_probability
    
    def perceive(self, environment: Any) -> Perception:
        """
        Percibe el entorno (muy limitado para agente reflejo simple)
        """
        from src.environment.space import Position
        
        current_pos = Position(*self.state.position)
        
        adjacent_positions = environment.get_adjacent_positions(current_pos)
        free_adjacent = [pos for pos in adjacent_positions 
                        if environment.is_free(pos) and pos not in environment.robot_positions]
        
        sensor_data = {
            'position': self.state.position,
            'free_adjacent_cells': len(free_adjacent),
            'can_move': len(free_adjacent) > 0
        }
        
        return Perception(
            timestamp=self.state.iteration_count,
            sensor_data=sensor_data
        )
    
    def decide(self, perception: Perception) -> Action:
        """
        Decide la acción (movimiento aleatorio o quedarse quieto)
        """
        if not self.should_attempt_movement(perception.timestamp):
            return Action('stay', {})
        
        if not perception.sensor_data.get('can_move', False):
            return Action('stay', {'reason': 'no_free_cells'})
        
        return Action('move', {'random': True})
    
    def execute(self, action: Action, environment: Any) -> bool:
        """
        Ejecuta la acción en el entorno
        """
        from src.environment.space import Position, CellType
        
        if action.action_type == 'stay':
            return True
        
        if action.action_type == 'move':
            current_pos = Position(*self.state.position)
            
            adjacent_positions = environment.get_adjacent_positions(current_pos)
            free_adjacent = [pos for pos in adjacent_positions 
                           if environment.is_free(pos) and pos not in environment.robot_positions]
            
            if not free_adjacent:
                return False
            
            new_pos = self.random_state.choice(free_adjacent)
            
            success = environment.move_entity(current_pos, new_pos, CellType.MONSTER)
            
            if success:
                self.state.position = new_pos.to_tuple()
                action.parameters['new_position'] = self.state.position
            
            return success
        
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del monstruo
        """
        return {
            'agent_id': self.agent_id,
            'position': self.state.position,
            'is_active': self.state.is_active,
            'movements_made': self.state.movements_made,
            'last_movement_iteration': self.state.last_movement_iteration
        }