from dataclasses import dataclass
from typing import Tuple

@dataclass
class EnvironmentConfig:
    """
    Configuración del entorno de operación 3D
    """
    N: int = 10
    P_free: float = 0.70
    P_void: float = 0.30

    def __post_init__(self):
        if not (0 <= self.P_free <= 1 and 0 <= self.P_void <= 1):
            raise ValueError("Probabilidades deben estar entre 0 y 1")
        if abs(self.P_free + self.P_void - 1.0) > 0.01:
            raise ValueError("P_free + P_void debe ser igual a 1.0")


@dataclass
class AgentsConfig:
    """
    Configuración de los agentes del sistema
    """
    N_robots: int = 5
    N_monsters: int = 10
    monster_movement_frequency: int = 3
    monster_movement_probability: float = 1

    def __post_init__(self):
        if self.N_robots < 1:
            raise ValueError("Debe haber al menos 1 robot")
        if self.N_monsters < 1:
            raise ValueError("Debe haber al menos 1 monstruo")


@dataclass
class SimulationConfig:
    """
    Configuración de la simulación
    """
    max_iterations: int = 300
    save_images: bool = True
    images_dir: str = "reports/images"
    generate_report: bool = True
    report_path: str = "reports/simulation_report.md"
    random_seed: int = 42


class SystemConfig:
    """
    Configuración global del sistema
    """
    def __init__(self):
        self.environment = EnvironmentConfig()
        self.agents = AgentsConfig()
        self.simulation = SimulationConfig()

    @classmethod
    def custom(cls, n: int = 20, n_robots: int = 5, n_monsters: int = 10,
               max_iterations: int = 100) -> 'SystemConfig':
        """
        Crea una configuración personalizada del sistema
        """
        config = cls()
        config.environment.N = n
        config.agents.N_robots = n_robots
        config.agents.N_monsters = n_monsters
        config.simulation.max_iterations = max_iterations
        return config