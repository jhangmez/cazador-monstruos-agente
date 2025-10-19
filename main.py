import numpy as np
import sys
import os
from datetime import datetime
import pytz

from config import SystemConfig
from src.environment.space import OperationalSpace, Position
from src.agents.robot_agent import RobotAgent
from src.agents.monster_agent import MonsterAgent
from simulation.simulator import Simulator
from simulation.report_generator import ReportGenerator


def initialize_system(config: SystemConfig):
    """
    Inicializa el sistema completo con entorno y agentes
    """
    print("=" * 70)
    print("SISTEMA MULTI-AGENTE: CAZADORES DE MONSTRUOS")
    print("=" * 70)
    print()

    random_state = np.random.RandomState(config.simulation.random_seed)

    print("Creando entorno 3D...")
    environment = OperationalSpace(
        n=config.environment.N,
        p_free=config.environment.P_free,
        random_state=random_state
    )

    print(f"  - Dimensiones: {config.environment.N}³ = {config.environment.N ** 3} celdas")
    print(f"  - Zonas libres: ~{int(config.environment.N ** 3 * config.environment.P_free)}")
    print(f"  - Zonas vacías: ~{int(config.environment.N ** 3 * config.environment.P_void)}")
    print()

    print("Creando agentes robots...")
    robots = []
    for i in range(config.agents.N_robots):
        pos = environment.get_random_free_position()
        if pos:
            robot = RobotAgent(f"robot_{i}", pos.to_tuple())
            robots.append(robot)
            print(f"  - Robot {i+1} inicializado en {pos.to_tuple()}")

    print()
    print("Creando agentes monstruos...")
    monsters = []
    for i in range(config.agents.N_monsters):
        pos = environment.get_random_free_position()
        if pos:
            monster = MonsterAgent(
                f"monster_{i}",
                pos.to_tuple(),
                movement_frequency=config.agents.monster_movement_frequency,
                movement_probability=config.agents.monster_movement_probability,
                random_state=random_state
            )
            monsters.append(monster)
            print(f"  - Monstruo {i+1} inicializado en {pos.to_tuple()}")

    print()
    print(f"Sistema inicializado correctamente:")
    print(f"  - {len(robots)} robots activos")
    print(f"  - {len(monsters)} monstruos en el entorno")
    print()

    return environment, robots, monsters


def run_simulation(config: SystemConfig):
    """
    Ejecuta la simulación completa del sistema
    """
    environment, robots, monsters = initialize_system(config)

    print("=" * 70)
    print("INICIANDO SIMULACIÓN")
    print("=" * 70)
    print()

    simulator = Simulator(environment, robots, monsters, config)

    metrics = simulator.run()

    print()
    print("=" * 70)
    print("GENERANDO ESTADÍSTICAS")
    print("=" * 70)
    print()

    statistics = simulator.get_detailed_statistics()

    print("Resumen de la simulación:")
    summary = statistics['simulation_summary']
    print(f"  - Iteraciones ejecutadas: {summary['total_iterations']}")
    print(f"  - Robots finales: {summary['final_robots']}/{summary['initial_robots']}")
    print(f"  - Monstruos destruidos: {summary['total_monsters_destroyed']}/{summary['initial_monsters']}")
    print(f"  - Exploración máxima: {summary['max_exploration']:.2f}%")
    print()

    if config.simulation.generate_report:
        print("=" * 70)
        print("GENERANDO REPORTE")
        print("=" * 70)
        print()

        report_gen = ReportGenerator(config.simulation.report_path)
        report_path = report_gen.generate_report(
            config,
            statistics,
            metrics,
            metrics.events
        )

        print(f"Reporte completo disponible en: {report_path}")

    print()
    print("=" * 70)
    print("SIMULACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 70)

    return statistics, metrics


def main():
    """
    Función principal del programa
    """
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║   FUNDAMENTOS DE INTELIGENCIA ARTIFICIAL - EXAMEN PARCIAL    ║")
    print("║          Sistema Multi-Agente de Caza de Monstruos           ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print("\n")

    config = SystemConfig.custom(
        n=15,
        n_robots=5,
        n_monsters=10,
        max_iterations=100
    )

    gmt_minus_5 = pytz.timezone('Etc/GMT+5')

    timestamp = datetime.now(gmt_minus_5).strftime('%Y-%m-%d_%H-%M-%S')
    run_folder_name = f"ejecucion_{timestamp}"

    base_run_path = os.path.join('reports', run_folder_name)
    dynamic_report_path = os.path.join(base_run_path, 'simulation_report.md')
    dynamic_images_dir = os.path.join(base_run_path, 'images')

    config.simulation.report_path = dynamic_report_path
    config.simulation.images_dir = dynamic_images_dir

    print(f"Los resultados de esta ejecución se guardarán en: {base_run_path}")
    print("-" * 70)

    try:
        statistics, metrics = run_simulation(config)

        print("\n✓ Programa ejecutado exitosamente")
        print(f"✓ Archivos generados en: {config.simulation.images_dir}")
        print(f"✓ Reporte disponible en: {config.simulation.report_path}")

    except Exception as e:
        print(f"\n✗ Error durante la ejecución: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()