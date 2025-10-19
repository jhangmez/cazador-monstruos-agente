import os
from typing import List, Dict, Any, Tuple
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from collections import Counter

# Para evitar importaciones circulares, usaremos los tipos directamente
# El simulador pasará las instancias de las clases necesarias.
from .space import OperationalSpace, CellType, Position

# Establecemos un estilo visual agradable para los gráficos
plt.style.use('seaborn-v0_8-darkgrid')

class EnvironmentVisualizer:
    """
    Clase responsable de generar todas las visualizaciones de la simulación.
    """

    def __init__(self, images_dir: str):
        """
        Inicializa el visualizador.

        Args:
            images_dir (str): El directorio donde se guardarán las imágenes generadas.
        """
        self.output_dir = images_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _save_plot(self, fig, filename: str):
        """
        Guarda una figura en el directorio de salida y la cierra para liberar memoria.
        """
        path = os.path.join(self.output_dir, filename)
        fig.savefig(path, dpi=100, bbox_inches='tight')
        plt.close(fig)
        print(f"  - Visualización guardada en: {path}")

    def plot_3d_environment(self, environment: OperationalSpace, robots: List[Any], 
                            monsters: List[Any], iteration: int, filename: str = None):
        """
        Genera un gráfico 3D del estado actual del entorno.
        """
        if filename is None:
            filename = f"environment_iter_{iteration:04d}.png"

        fig = plt.figure(figsize=(12, 12))
        ax = fig.add_subplot(111, projection='3d')

        # Extraer posiciones
        robot_pos = [r.state.position for r in robots if r.is_active()]
        monster_pos = [m.state.position for m in monsters if m.is_active()]
        void_pos = [p.to_tuple() for p in environment.void_positions]

        # Graficar Zonas Vacías
        if void_pos:
            vx, vy, vz = zip(*void_pos)
            ax.scatter(vx, vy, vz, c='grey', marker='s', s=15, alpha=0.1, label='Zona Vacía')

        # Graficar Monstruos
        if monster_pos:
            mx, my, mz = zip(*monster_pos)
            ax.scatter(mx, my, mz, c='red', marker='^', s=100, depthshade=True, label='Monstruo')

        # Graficar Robots
        if robot_pos:
            rx, ry, rz = zip(*robot_pos)
            ax.scatter(rx, ry, rz, c='blue', marker='o', s=100, depthshade=True, label='Robot')

        # Configuración del gráfico
        ax.set_title(f"Estado del Entorno en Iteración {iteration}", fontsize=16)
        ax.set_xlabel("Eje X")
        ax.set_ylabel("Eje Y")
        ax.set_zlabel("Eje Z")
        n = environment.n
        ax.set_xlim(0, n)
        ax.set_ylim(0, n)
        ax.set_zlim(0, n)
        ax.legend()
        ax.grid(True)

        self._save_plot(fig, filename)

    def plot_statistics(self, metrics: Dict[str, List], filename: str):
        """
        Grafica la evolución de las métricas de la simulación a lo largo del tiempo.
        """
        fig, ax1 = plt.subplots(figsize=(12, 7))

        iterations = range(len(metrics['robots_active']))

        # Eje principal (izquierda)
        ax1.plot(iterations, metrics['robots_active'], label='Robots Activos', color='blue')
        ax1.plot(iterations, metrics['monsters_alive'], label='Monstruos Vivos', color='red')
        ax1.plot(iterations, metrics['monsters_destroyed'], label='Monstruos Destruidos', color='green', linestyle='--')

        ax1.set_xlabel("Iteración")
        ax1.set_ylabel("Cantidad de Entidades")
        ax1.tick_params(axis='y')

        # Eje secundario (derecha) para la cobertura de exploración
        ax2 = ax1.twinx()
        ax2.plot(iterations, metrics['exploration_coverage'], label='Cobertura de Exploración (%)', color='purple', linestyle=':')
        ax2.set_ylabel("Exploración (%)", color='purple')
        ax2.tick_params(axis='y', labelcolor='purple')
        ax2.set_ylim(0, 100)

        fig.suptitle("Evolución de Métricas de la Simulación", fontsize=16)
        fig.legend(loc="upper right", bbox_to_anchor=(0.9, 0.9))
        fig.tight_layout(rect=[0, 0, 1, 0.96])

        self._save_plot(fig, filename)

    def plot_heatmap(self, all_positions: List[Tuple[int, int, int]], n: int, filename: str):
        """
        Genera un mapa de calor 2D proyectado de las posiciones visitadas por los robots.
        """
        if not all_positions:
            return

        counts = Counter(all_positions)

        heatmap_xy = np.zeros((n, n))
        heatmap_xz = np.zeros((n, n))
        heatmap_yz = np.zeros((n, n))

        for (x, y, z), count in counts.items():
            heatmap_xy[y, x] += count
            heatmap_xz[z, x] += count
            heatmap_yz[z, y] += count

        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 6))

        # Proyección XY (Vista Superior)
        im1 = ax1.imshow(heatmap_xy, cmap='viridis', origin='lower')
        ax1.set_title("Proyección XY (Vista Superior)")
        ax1.set_xlabel("Eje X")
        ax1.set_ylabel("Eje Y")

        # Proyección XZ (Vista Frontal)
        im2 = ax2.imshow(heatmap_xz, cmap='viridis', origin='lower')
        ax2.set_title("Proyección XZ (Vista Frontal)")
        ax2.set_xlabel("Eje X")
        ax2.set_ylabel("Eje Z")

        # Proyección YZ (Vista Lateral)
        im3 = ax3.imshow(heatmap_yz, cmap='viridis', origin='lower')
        ax3.set_title("Proyección YZ (Vista Lateral)")
        ax3.set_xlabel("Eje Y")
        ax3.set_ylabel("Eje Z")

        fig.colorbar(im1, ax=[ax1, ax2, ax3], orientation='vertical', fraction=0.02, pad=0.04)
        fig.suptitle("Mapa de Calor de Exploración de Robots", fontsize=16)
        fig.tight_layout(rect=[0, 0, 1, 0.95])

        self._save_plot(fig, filename)

    def plot_2d_slices(self, environment: OperationalSpace, robots: List[Any],
                       monsters: List[Any], z_level: int, iteration: int, filename: str):
        """
        Grafica un corte transversal 2D del entorno en un nivel Z específico.
        """
        fig, ax = plt.subplots(figsize=(10, 10))

        # Crear una matriz para el fondo (zonas libres vs vacías)
        slice_grid = np.zeros((environment.n, environment.n))
        for x in range(environment.n):
            for y in range(environment.n):
                pos = Position(x, y, z_level)
                if environment.is_void(pos):
                    slice_grid[y, x] = 1 # 1 para vacío

        ax.imshow(slice_grid, cmap='Greys', origin='lower', alpha=0.3)

        # Extraer y graficar entidades en este nivel
        robot_pos_slice = [(r.state.position[0], r.state.position[1]) for r in robots if r.is_active() and r.state.position[2] == z_level]
        monster_pos_slice = [(m.state.position[0], m.state.position[1]) for m in monsters if m.is_active() and m.state.position[2] == z_level]

        if robot_pos_slice:
            rx, ry = zip(*robot_pos_slice)
            ax.scatter(rx, ry, c='blue', marker='o', s=150, label='Robot')

        if monster_pos_slice:
            mx, my = zip(*monster_pos_slice)
            ax.scatter(mx, my, c='red', marker='^', s=150, label='Monstruo')

        # Configuración del gráfico
        ax.set_title(f"Corte Transversal en Z={z_level} (Iteración {iteration})", fontsize=16)
        ax.set_xlabel("Eje X")
        ax.set_ylabel("Eje Y")
        ax.set_xlim(-0.5, environment.n - 0.5)
        ax.set_ylim(-0.5, environment.n - 0.5)
        ax.set_xticks(np.arange(0, environment.n, 2))
        ax.set_yticks(np.arange(0, environment.n, 2))
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.legend()

        self._save_plot(fig, filename)