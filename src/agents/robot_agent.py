from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from dataclasses import dataclass
import sys
sys.path.append('..')

from .base_agent import BaseAgent, AgentState, Perception, Action


@dataclass
class RobotOrientation:
    """
    Orientación del robot en el espacio 3D
    """
    forward: Tuple[int, int, int]

    def rotate_90(self, side: int) -> 'RobotOrientation':
        """
        Rota la orientación 90 grados hacia uno de los lados
        """
        fx, fy, fz = self.forward

        if fx != 0:
            if side == 0:
                return RobotOrientation((0, fx, 0))
            elif side == 1:
                return RobotOrientation((0, -fx, 0))
            elif side == 2:
                return RobotOrientation((0, 0, fx))
            else:
                return RobotOrientation((0, 0, -fx))
        elif fy != 0:
            if side == 0:
                return RobotOrientation((fy, 0, 0))
            elif side == 1:
                return RobotOrientation((-fy, 0, 0))
            elif side == 2:
                return RobotOrientation((0, 0, fy))
            else:
                return RobotOrientation((0, 0, -fy))
        else:
            if side == 0:
                return RobotOrientation((fz, 0, 0))
            elif side == 1:
                return RobotOrientation((-fz, 0, 0))
            elif side == 2:
                return RobotOrientation((0, fz, 0))
            else:
                return RobotOrientation((0, -fz, 0))

    def get_front_position(self, current_pos: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """
        Calcula la posición frontal basada en la orientación
        """
        x, y, z = current_pos
        fx, fy, fz = self.forward
        return (x + fx, y + fy, z + fz)

    def get_surrounding_positions(self, current_pos: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        """
        Obtiene las 5 posiciones alrededor del robot (excluyendo parte posterior)
        """
        x, y, z = current_pos
        fx, fy, fz = self.forward

        positions = [
            (x + fx, y + fy, z + fz)
        ]

        directions = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
        back = (-fx, -fy, -fz)

        for dx, dy, dz in directions:
            if (dx, dy, dz) != back and (dx, dy, dz) != (fx, fy, fz):
                positions.append((x + dx, y + dy, z + dz))

        return positions[:5]


class RobotState(AgentState):
    """
    Estado interno del robot con memoria
    """

    def __init__(self, agent_id: str, initial_position: Tuple[int, int, int]):
        super().__init__(agent_id)
        self.position = initial_position
        self.orientation = RobotOrientation((1, 0, 0))

        from ..memory.perception_action_table import PerceptionActionTable
        self.memory = PerceptionActionTable()

        self.known_void_zones: set[Tuple[int, int, int]] = set()
        self.just_collided: bool = False
        self.monsters_destroyed = 0
        self.collisions_with_void = 0
        self.movements_made = 0
        self.rotations_made = 0
        self.current_rotation_side = 0

    def update(self, perception: Perception, action: Action):
        """
        Actualiza el estado del robot con nueva percepción y acción
        """
        self.just_collided = False
        if action.action_type == 'move' and action.success:
            self.movements_made += 1

        if action.action_type == 'move' and action.parameters.get('hit_void', False):
            front_pos = self.orientation.get_front_position(self.position)
            self.known_void_zones.add(front_pos)

        if action.action_type == 'rotate':
            self.rotations_made += 1

        if action.action_type == 'destroy':
            self.monsters_destroyed += 1

        if action.parameters.get('hit_void', False):
            self.collisions_with_void += 1

        self.memory.add_entry(
            timestamp=perception.timestamp,
            position=self.position,
            perception=perception.sensor_data,
            action=action.action_type,
            action_params=action.parameters,
            success=action.success
        )


class RobotAgent(BaseAgent):
    """
    Agente robot cazador de monstruos con memoria interna
    """

    def __init__(self, agent_id: str, initial_position: Tuple[int, int, int]):
        self.initial_position = initial_position
        super().__init__(agent_id)

    def _initialize_state(self) -> RobotState:
        """
        Inicializa el estado del robot
        """
        return RobotState(self.agent_id, self.initial_position)

    def perceive(self, environment: Any) -> Perception:
        """
        Percibe el entorno usando sus sensores
        """
        from src.environment.space import Position

        current_pos = Position(*self.state.position)
        sensor_data = {}

        sensor_data['position'] = self.state.position
        sensor_data['orientation'] = self.state.orientation.forward

        surrounding = self.state.orientation.get_surrounding_positions(self.state.position)
        monster_nearby = False

        for pos_tuple in surrounding:
            pos = Position(*pos_tuple)
            if pos.is_valid(environment.n):
                if pos in environment.monster_positions:
                    monster_nearby = True
                    break

        sensor_data['monster_detected'] = monster_nearby

        current_cell_pos = Position(*self.state.position)
        sensor_data['monster_in_cell'] = current_cell_pos in environment.monster_positions

        front_pos = self.state.orientation.get_front_position(self.state.position)
        front_position = Position(*front_pos)
        sensor_data['robot_ahead'] = front_position in environment.robot_positions

        sensor_data['hit_void'] = False
        sensor_data['attempted_position'] = None

        return Perception(
            timestamp=self.state.iteration_count,
            sensor_data=sensor_data
        )

    def decide(self, perception: Perception) -> Action:
        """
        Decide la acción a tomar basándose en una jerarquía de prioridades.
        """
        sensor_data = perception.sensor_data

        # PRIORIDAD 0: REACCIÓN A COLISIÓN (La más urgente)
        # Si acabamos de chocar, la única acción sensata es rotar.
        if self.state.just_collided:
            # El flag se resetea en el siguiente 'update', así que solo reaccionamos.
            side = self.state.current_rotation_side % 4
            self.state.current_rotation_side += 1
            return Action('rotate', {'reason': 'priority_0_collision_reaction'})

        # PRIORIDAD 1: DESTRUCCIÓN
        if sensor_data.get('monster_in_cell', False):
            return Action('destroy', {'reason': 'priority_1_monster_in_cell'})

        # PRIORIDAD 2: NEGOCIACIÓN
        if sensor_data.get('robot_ahead', False):
            return self._handle_robot_collision()

        # PRIORIDAD 3: MODO CAZA
        if sensor_data.get('monster_detected', False):
            return self._move_towards_monster(sensor_data)

        # PRIORIDAD 4: MODO EXPLORACIÓN (Acción por defecto)
        return self._explore_space()

    def _handle_robot_collision(self) -> Action:
        """
        Maneja la colisión con otro robot
        """
        import random
        decision = random.choice(['both_rotate', 'one_continues'])

        if decision == 'both_rotate':
            side = (self.state.current_rotation_side % 4)
            self.state.current_rotation_side += 1
            return Action('rotate', {'side': side, 'reason': 'robot_collision'})
        else:
            return Action('move', {'reason': 'robot_collision_continue'})

    def _move_towards_monster(self, sensor_data: Dict) -> Action:
        """
        """
        return Action('move', {'reason': 'hunting_probe'})


    def _explore_space(self) -> Action:
        """
        Explora el espacio usando la memoria para tomar decisiones inteligentes.
        """
        front_pos = self.state.orientation.get_front_position(self.state.position)

        if front_pos in self.state.known_void_zones:
            side = self.state.current_rotation_side % 4
            self.state.current_rotation_side += 1
            return Action('rotate', {'side': side, 'reason': 'explore_avoid_known_void'})

        visit_count = self.state.memory.count_visits_to_position(front_pos)
        if visit_count > 5:
            side = self.state.current_rotation_side % 4
            self.state.current_rotation_side += 1
            return Action('rotate', {'side': side, 'reason': 'explore_avoid_loop'})

        return Action('move', {'reason': 'exploring_new_path'})

    def execute(self, action: Action, environment: Any) -> bool:
        """
        Ejecuta la acción en el entorno y actualiza la percepción si hay colisión.
        """
        if action.action_type == 'move':
            success, hit_void = self._execute_move(environment)
            if hit_void:
                self.state.just_collided = True
                action.parameters['hit_void'] = True
            return success

        elif action.action_type == 'rotate':
            return self._execute_rotate(action)
        elif action.action_type == 'destroy':
            return self._execute_destroy(environment)

        return False

    def _execute_move(self, environment: Any) -> Tuple[bool, bool]:
        """
        Ejecuta el movimiento del robot.
        Retorna (éxito_del_movimiento, choco_con_vacio)
        """
        from ..environment.space import Position, CellType

        current_pos = Position(*self.state.position)
        front_pos_tuple = self.state.orientation.get_front_position(self.state.position)
        front_pos = Position(*front_pos_tuple)

        if not front_pos.is_valid(environment.n):
            return False, True

        if environment.is_void(front_pos):
            return False, True

        if front_pos in environment.robot_positions:
            return False, False

        success = environment.move_entity(current_pos, front_pos, CellType.ROBOT)
        if success:
            self.state.position = front_pos_tuple

        return success, False

    def _execute_rotate(self, action: Action) -> bool:
        """
        Ejecuta la rotación del robot
        """
        side = action.parameters.get('side', 0)
        self.state.orientation = self.state.orientation.rotate_90(side)
        return True

    def _execute_destroy(self, environment: Any) -> bool:
        """
        Ejecuta la destrucción del monstruo y del robot,
        y desactiva al agente monstruo correspondiente.
        """
        from ..environment.space import Position

        current_pos = Position(*self.state.position)

        if current_pos in environment.monster_positions:
            monster_to_destroy = None
            if hasattr(environment, 'monsters'):
                for monster in environment.monsters:
                    if monster.is_active() and monster.state.position == self.state.position:
                        monster_to_destroy = monster
                        break

            environment.destroy_cell(current_pos)

            if monster_to_destroy:
                monster_to_destroy.deactivate()

            self.deactivate()
            return True

        return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del robot
        """
        return {
            'agent_id': self.agent_id,
            'position': self.state.position,
            'is_active': self.state.is_active,
            'monsters_destroyed': self.state.monsters_destroyed,
            'movements_made': self.state.movements_made,
            'rotations_made': self.state.rotations_made,
            'collisions_with_void': self.state.collisions_with_void,
            'memory_statistics': self.state.memory.get_statistics()
        }