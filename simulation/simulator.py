from typing import List, Dict, Any, Tuple
import numpy as np
from dataclasses import dataclass, field
import time


@dataclass
class SimulationEvent:
    """
    Representa un evento durante la simulación
    """
    iteration: int
    event_type: str
    agent_id: str
    description: str
    data: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self):
        return f"[{self.iteration}] {self.event_type}: {self.description}"


class SimulationMetrics:
    """
    Métricas y estadísticas de la simulación
    """
    
    def __init__(self):
        self.robots_active = []
        self.monsters_alive = []
        self.monsters_destroyed = []
        self.total_movements = []
        self.exploration_coverage = []
        self.events: List[SimulationEvent] = []
    
    def record_iteration(self, iteration: int, robots: List, monsters: List,
                        total_movements: int, exploration: float):
        """
        Registra las métricas de una iteración
        """
        active_robots = sum(1 for r in robots if r.is_active())
        alive_monsters = sum(1 for m in monsters if m.is_active())
        destroyed = len(monsters) - alive_monsters
        
        self.robots_active.append(active_robots)
        self.monsters_alive.append(alive_monsters)
        self.monsters_destroyed.append(destroyed)
        self.total_movements.append(total_movements)
        self.exploration_coverage.append(exploration)
    
    def add_event(self, event: SimulationEvent):
        """
        Añade un evento a la historia
        """
        self.events.append(event)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen de las métricas
        """
        return {
            'total_iterations': len(self.robots_active),
            'initial_robots': self.robots_active[0] if self.robots_active else 0,
            'final_robots': self.robots_active[-1] if self.robots_active else 0,
            'initial_monsters': self.monsters_alive[0] if self.monsters_alive else 0,
            'final_monsters': self.monsters_alive[-1] if self.monsters_alive else 0,
            'total_monsters_destroyed': self.monsters_destroyed[-1] if self.monsters_destroyed else 0,
            'total_movements': sum(self.total_movements),
            'max_exploration': max(self.exploration_coverage) if self.exploration_coverage else 0,
            'total_events': len(self.events)
        }
    
    def to_dict(self) -> Dict[str, List]:
        """
        Convierte las métricas a diccionario
        """
        return {
            'robots_active': self.robots_active,
            'monsters_alive': self.monsters_alive,
            'monsters_destroyed': self.monsters_destroyed,
            'total_movements': self.total_movements,
            'exploration_coverage': self.exploration_coverage
        }


class Simulator:
    """
    Motor principal de simulación del sistema multi-agente
    """
    
    def __init__(self, environment, robots: List, monsters: List, config):
        """
        Inicializa el simulador
        """
        self.environment = environment
        self.robots = robots
        self.monsters = monsters
        self.config = config
        self.environment.monsters = self.monsters
        self.metrics = SimulationMetrics()
        self.current_iteration = 0
        
        from src.environment.visualizer import EnvironmentVisualizer
        self.visualizer = EnvironmentVisualizer(config.simulation.images_dir)
    
    def initialize_entities(self):
        """
        Inicializa las entidades en el entorno
        """
        for robot in self.robots:
            from src.environment.space import Position
            pos = Position(*robot.state.position)
            self.environment.set_robot(pos)
        
        for monster in self.monsters:
            from src.environment.space import Position
            pos = Position(*monster.state.position)
            self.environment.set_monster(pos)
    
    def run_iteration(self) -> bool:
        """
        Ejecuta una iteración completa de la simulación
        """
        active_robots = [r for r in self.robots if r.is_active()]
        active_monsters = [m for m in self.monsters if m.is_active()]
        
        if not active_robots or not active_monsters:
            return False
        
        iteration_movements = 0
        
        for robot in active_robots:
            perception, action, success = robot.operate(self.environment)
            
            if action:
                if action.action_type == 'move' and success:
                    iteration_movements += 1
                
                if action.action_type == 'destroy' and success:
                    event = SimulationEvent(
                        iteration=self.current_iteration,
                        event_type='MONSTER_DESTROYED',
                        agent_id=robot.agent_id,
                        description=f'Robot {robot.agent_id[:8]} destruyó un monstruo',
                        data={'position': robot.state.position}
                    )
                    self.metrics.add_event(event)
        
        for monster in active_monsters:
            perception, action, success = monster.operate(self.environment)
            
            if action and action.action_type == 'move' and success:
                iteration_movements += 1
        
        total_positions = self.environment.n ** 3
        all_positions = []
        for robot in self.robots:
            if hasattr(robot.state, 'memory'):
                all_positions.extend(robot.state.memory.position_history)
        
        exploration = (len(set(all_positions)) / total_positions) * 100 if all_positions else 0
        
        self.metrics.record_iteration(
            self.current_iteration,
            self.robots,
            self.monsters,
            iteration_movements,
            exploration
        )
        
        return True
    
    def run(self) -> SimulationMetrics:
        """
        Ejecuta la simulación completa
        """
        print(f"Iniciando simulación...")
        print(f"Configuración: N={self.environment.n}, Robots={len(self.robots)}, Monstruos={len(self.monsters)}")
        
        self.initialize_entities()
        
        if self.config.simulation.save_images:
            self.visualizer.plot_3d_environment(
                self.environment,
                self.robots,
                self.monsters,
                0,
                "initial_state.png"
            )
        
        start_time = time.time()
        
        for iteration in range(self.config.simulation.max_iterations):
            self.current_iteration = iteration
            
            if not self.run_iteration():
                print(f"\nSimulación terminada en iteración {iteration}")
                break
            
            if (iteration + 1) % 10 == 0:
                active_robots = sum(1 for r in self.robots if r.is_active())
                active_monsters = sum(1 for m in self.monsters if m.is_active())
                print(f"Iteración {iteration + 1}: Robots={active_robots}, Monstruos={active_monsters}")
            
            if self.config.simulation.save_images and (iteration + 1) % 20 == 0:
                self.visualizer.plot_3d_environment(
                    self.environment,
                    self.robots,
                    self.monsters,
                    iteration + 1
                )
        
        elapsed_time = time.time() - start_time
        
        if self.config.simulation.save_images:
            self.visualizer.plot_3d_environment(
                self.environment,
                self.robots,
                self.monsters,
                self.current_iteration,
                "final_state.png"
            )
            
            self.visualizer.plot_statistics(
                self.metrics.to_dict(),
                "statistics.png"
            )
            
            all_positions = []
            for robot in self.robots:
                if hasattr(robot.state, 'memory'):
                    all_positions.extend(robot.state.memory.position_history)
            
            if all_positions:
                self.visualizer.plot_heatmap(
                    all_positions,
                    self.environment.n,
                    "exploration_heatmap.png"
                )
            
            middle_z = self.environment.n // 2
            self.visualizer.plot_2d_slices(
                self.environment,
                self.robots,
                self.monsters,
                middle_z,
                self.current_iteration,
                "slice_middle.png"
            )
        
        print(f"\nSimulación completada en {elapsed_time:.2f} segundos")
        print(f"Iteraciones ejecutadas: {self.current_iteration + 1}")
        
        return self.metrics
    
    def get_detailed_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas detalladas de la simulación
        """
        robot_stats = [r.get_statistics() for r in self.robots]
        monster_stats = [m.get_statistics() for m in self.monsters]
        
        total_monsters_destroyed = sum(1 for r in self.robots if not r.is_active())
        
        return {
            'simulation_summary': self.metrics.get_summary(),
            'robot_statistics': robot_stats,
            'monster_statistics': monster_stats,
            'environment_info': {
                'size': self.environment.n,
                'entity_counts': self.environment.count_entities()
            },
            'performance': {
                'total_monsters_destroyed': total_monsters_destroyed,
                'robots_sacrificed': len(self.robots) - sum(1 for r in self.robots if r.is_active()),
                'destruction_efficiency': total_monsters_destroyed / len(self.robots) if self.robots else 0
            }
        }