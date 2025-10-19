# Sistema Multi-Agente: Caza de Monstruos en un Entorno 3D

## 1. Descripción del Proyecto

Este proyecto implementa un **Sistema Multi-Agente (SMA)** en un entorno tridimensional discreto, simulando un escenario de "caza". El sistema está diseñado como parte del curso de **Fundamentos de Inteligencia Artificial** y sigue los principios de diseño de agentes inteligentes descritos por AIMA (Russell & Norvig).

El objetivo principal es que un equipo de **agentes Robot** autónomos, equipados con memoria interna, exploren un espacio desconocido para localizar y destruir a un conjunto de **agentes Monstruo** de comportamiento estocástico.

## 2. Ontología y Conceptos Clave

El universo de la simulación se rige por los siguientes conceptos:

- **Entorno de Operación:** Un espacio cúbico de `N x N x N` celdas.
  - **Zonas Libres:** Espacios navegables.
  - **Zonas Vacías:** Obstáculos impenetrables que los robots solo pueden descubrir al chocar contra ellos.
- **Agente Robot (Agente con Memoria Interna):**
  - **Objetivo:** Maximizar el número de monstruos destruidos.
  - **Percepción:** Limitada a su entorno inmediato (sensores de proximidad para monstruos y robots, sensor de colisión con muros).
  - **Memoria:** Almacena un historial de percepciones y acciones (`Tabla Percepción-Acción`) que utiliza para tomar decisiones más informadas, como evitar obstáculos ya conocidos y explorar áreas nuevas.
  - **Comportamiento:** Sigue un ciclo **Percepción-Decisión-Acción**, operando bajo una jerarquía de reglas: `Destruir > Negociar > Cazar > Explorar`.
  - **Sacrificio:** Para destruir un monstruo, el robot debe ocupar la misma celda y autodestruirse, convirtiendo la celda en una Zona Vacía.
- **Agente Monstruo (Agente de Reflejo Simple):**
  - **Comportamiento:** No tiene memoria ni objetivos complejos. Su única acción es moverse aleatoriamente a una celda adyacente libre con una probabilidad `p` cada `K` iteraciones.
  - **Naturaleza:** Entidades energéticas que irradian una señal detectable por los robots.

## 3. Arquitectura del Proyecto

El código está organizado en una estructura modular para separar responsabilidades:

```
.
├── reports/                  # Carpeta de salida para los reportes y visualizaciones
├── simulation/
│   ├── simulator.py          # Motor principal de la simulación
│   └── report_generator.py   # Generador de reportes en Markdown
├── src/
│   ├── agents/
│   │   ├── base_agent.py     # Clases abstractas para todos los agentes
│   │   ├── robot_agent.py    # Implementación del agente Robot
│   │   └── monster_agent.py  # Implementación del agente Monstruo
│   ├── environment/
│   │   ├── space.py          # Lógica del entorno 3D (grid)
│   │   └── visualizer.py     # Generación de gráficos y mapas de calor
│   └── memory/
│       └── perception_action_table.py # Lógica de la memoria del robot
├── config.py                 # Clases de configuración para el sistema
├── main.py                   # Punto de entrada principal para ejecutar la simulación
└── requirements.txt          # Dependencias del proyecto
```

## 4. Instalación

Para ejecutar este proyecto, necesitas Python 3.8 o superior.

1.  **Clona el repositorio:**

    ```bash
    git clone <URL-DEL-REPOSITORIO>
    cd <NOMBRE-DEL-REPOSITORIO>
    ```

2.  **Crea un entorno virtual (recomendado):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
    Las dependencias principales son `numpy`, `matplotlib`, `pandas`, `seaborn` y `pytz`.

## 5. Cómo Ejecutar la Simulación

La simulación se ejecuta desde el archivo `main.py`.

```bash
python main.py
```

Al ejecutarlo, el programa realizará las siguientes acciones:

1.  Creará una carpeta de salida única dentro de `reports/` con la fecha y hora de la ejecución (ej: `reports/ejecucion_2023-10-27_15-30-00/`).
2.  Inicializará el entorno y los agentes según los parámetros definidos en `main.py`.
3.  Ejecutará la simulación iteración por iteración, mostrando el progreso en la consola.
4.  Al finalizar, guardará todas las visualizaciones (gráficos 3D, mapa de calor, etc.) en la subcarpeta `images/`.
5.  Generará un reporte completo en formato Markdown (`simulation_report.md`) que resume la configuración, el comportamiento de los agentes y los resultados.

### Configuración de la Simulación

Puedes modificar los parámetros principales de la simulación directamente en la función `main()` del archivo `main.py`:

```python
# En main.py
config = SystemConfig.custom(
    n=15,             # Tamaño del lado del cubo (entorno de 15x15x15)
    n_robots=5,       # Número de robots
    n_monsters=10,    # Número de monstruos
    max_iterations=200 # Límite de iteraciones para la simulación
)
```

## 6. Resultados Esperados

Una ejecución exitosa del programa debe producir los siguientes resultados:

- **Comportamiento Inteligente:**
  - Los **robots explorarán activamente** el entorno, incrementando el porcentaje de "Cobertura de Exploración".
  - Aprenderán la ubicación de las **Zonas Vacías** tras chocar con ellas y las evitarán en movimientos futuros.
  - Al detectar un monstruo, cambiarán a un **modo de caza**, buscando activamente en el área de la detección.
- **Destrucción de Monstruos:**
  - Se espera que los robots logren localizar y destruir a varios monstruos. El gráfico de "Estadísticas de la Simulación" mostrará una disminución en la línea de "Monstruos Vivos" y un aumento en "Monstruos Destruidos".
  - Cada destrucción irá acompañada de una disminución en el número de "Robots Activos".
- **Reporte Detallado:**
  - Se generará un **informe completo en Markdown** con todos los detalles de la simulación, incluyendo:
    - Parámetros de configuración.
    - Análisis del comportamiento de los agentes.
    - Métricas de rendimiento (eficiencia de destrucción, tasa de éxito, etc.).
    - Visualizaciones incrustadas que muestran el estado inicial y final del entorno, la evolución de las métricas y un mapa de calor de las zonas más exploradas.
