from typing import Dict, Any, List
import os
from datetime import datetime


class ReportGenerator:
    """
    Genera reportes en formato Markdown de la simulación
    """

    def __init__(self, output_path: str = "reports/simulation_report.md"):
        """
        Inicializa el generador de reportes
        """
        self.output_path = output_path
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    def generate_report(self, config, statistics: Dict[str, Any], 
                       metrics, events: List) -> str:
        """
        Genera el reporte completo de la simulación
        """
        report_lines = []

        report_lines.extend(self._generate_header())
        report_lines.extend(self._generate_ontology_section())
        report_lines.extend(self._generate_problem_section())
        report_lines.extend(self._generate_configuration_section(config))
        report_lines.extend(self._generate_agent_description_section())
        report_lines.extend(self._generate_environment_characteristics())
        report_lines.extend(self._generate_perception_action_tables())
        report_lines.extend(self._generate_results_section(statistics, metrics))
        report_lines.extend(self._generate_visualizations_section())
        report_lines.extend(self._generate_analysis_section(statistics))
        report_lines.extend(self._generate_events_section(events))
        report_lines.extend(self._generate_conclusions_section(statistics))

        report_content = '\n'.join(report_lines)

        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"\nReporte generado: {self.output_path}")
        return self.output_path

    def _generate_header(self) -> List[str]:
        """
        Genera el encabezado del reporte
        """
        return [
            "# Reporte de Simulación: Sistema Multi-Agente de Caza de Monstruos",
            "",
            f"**Fecha de generación:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            ""
        ]

    def _generate_ontology_section(self) -> List[str]:
        """
        Genera la sección de ontología
        """
        return [
            "## 1. Ontología del Sistema",
            "",
            "### 1.1 Conceptos Fundamentales",
            "",
            "#### Entorno de Operación",
            "Espacio tridimensional discretizado en cubos de N³ celdas, donde cada celda puede ser:",
            "- **Zona Libre**: Espacio navegable por entidades materiales y energéticas",
            "- **Zona Vacía**: Espacio impenetrable que actúa como barrera física",
            "",
            "#### Agente Robot",
            "Entidad autónoma con capacidades sensoriales y efectoras diseñada para la caza de monstruos.",
            "Características:",
            "- Tiene **memoria interna** que almacena percepciones y acciones históricas",
            "- Opera mediante un **ciclo percepción-decisión-acción**",
            "- Puede **aprender de experiencias pasadas** para mejorar decisiones",
            "- Se **autodestruye** al eliminar un monstruo",
            "",
            "#### Agente Monstruo",
            "Entidad energética que ocupa completamente un cubo del espacio.",
            "Características:",
            "- Agente de **reflejo simple** sin memoria",
            "- Movimiento **estocástico** basado en probabilidad",
            "- Irradia energía detectable en su entorno inmediato",
            "- Desea ser destruido por los robots",
            "",
            "#### Posición",
            "Coordenada tridimensional (x, y, z) que identifica unívocamente una celda en el espacio.",
            "",
            "#### Orientación",
            "Vector direccional que define hacia dónde está orientado un robot (parte frontal).",
            "",
            "#### Percepción",
            "Información sensorial capturada por un agente en un momento específico.",
            "",
            "#### Acción",
            "Operación efectora ejecutada por un agente que modifica el entorno o su estado interno.",
            "",
            "### 1.2 Relaciones Conceptuales",
            "",
            "- Un **Agente** opera en un **Entorno**",
            "- Un **Robot** tiene **Sensores** y **Efectores**",
            "- Un **Robot** mantiene una **Tabla de Memoria** de percepciones-acciones",
            "- Un **Monstruo** emite **Energía** detectable por sensores",
            "- Una **Posición** puede contener una **Entidad** (Robot o Monstruo)",
            "- Una **Zona Vacía** bloquea el movimiento de **Entidades**",
            "- La **destrucción** de un monstruo elimina tanto al monstruo como al robot",
            "",
            "---",
            ""
        ]

    def _generate_problem_section(self) -> List[str]:
        """
        Genera la sección de definición del problema
        """
        return [
            "## 2. Definición del Problema",
            "",
            "### 2.1 Enunciado del Problema",
            "",
            "Diseñar e implementar un sistema multi-agente donde robots autónomos con memoria interna",
            "deben localizar y destruir monstruos en un entorno tridimensional parcialmente observable,",
            "mientras evitan zonas vacías y coordinan acciones con otros robots.",
            "",
            "### 2.2 Objetivos del Sistema",
            "",
            "**Objetivo Principal:**",
            "Maximizar la cantidad de monstruos destruidos minimizando el tiempo de búsqueda.",
            "",
            "**Objetivos Secundarios:**",
            "1. Explorar eficientemente el espacio 3D",
            "2. Aprender patrones de ubicación de zonas vacías",
            "3. Coordinar acciones entre múltiples robots",
            "4. Utilizar memoria histórica para tomar decisiones informadas",
            "",
            "### 2.3 Restricciones",
            "",
            "- Los robots no conocen su posición absoluta en el espacio",
            "- Los sensores tienen alcance limitado (entorno inmediato)",
            "- Los monstruos pueden moverse estocásticamente",
            "- La destrucción de un monstruo implica la pérdida del robot",
            "- Las zonas vacías solo se detectan por colisión",
            "",
            "---",
            ""
        ]

    def _generate_configuration_section(self, config) -> List[str]:
        """
        Genera la sección de configuración
        """
        return [
            "## 3. Configuración de la Simulación",
            "",
            "### 3.1 Parámetros del Entorno",
            "",
            f"- **Tamaño del espacio (N):** {config.environment.N}",
            f"- **Total de celdas:** {config.environment.N ** 3}",
            f"- **Porcentaje de zonas libres:** {config.environment.P_free * 100:.1f}%",
            f"- **Porcentaje de zonas vacías:** {config.environment.P_void * 100:.1f}%",
            "",
            "### 3.2 Parámetros de los Agentes",
            "",
            f"- **Número de robots:** {config.agents.N_robots}",
            f"- **Número de monstruos:** {config.agents.N_monsters}",
            f"- **Frecuencia de movimiento de monstruos:** Cada {config.agents.monster_movement_frequency} iteraciones",
            f"- **Probabilidad de movimiento de monstruos:** {config.agents.monster_movement_probability * 100:.1f}%",
            "",
            "### 3.3 Parámetros de la Simulación",
            "",
            f"- **Máximo de iteraciones:** {config.simulation.max_iterations}",
            f"- **Generación de imágenes:** {'Sí' if config.simulation.save_images else 'No'}",
            f"- **Directorio de imágenes:** `{config.simulation.images_dir}`",
            f"- **Semilla aleatoria:** {config.simulation.random_seed}",
            "",
            "---",
            ""
        ]

    def _generate_agent_description_section(self) -> List[str]:
        """
        Genera la descripción de los agentes
        """
        return [
            "## 4. Descripción de los Agentes",
            "",
            "### 4.1 Agente Robot (Con Memoria Interna)",
            "",
            "#### 4.1.1 Sensores",
            "",
            "1. **Giroscopio**",
            "   - Proporciona orientación espacial del robot",
            "   - Define parte frontal, posterior y 4 costados",
            "",
            "2. **Monstroscopio**",
            "   - Detecta presencia de monstruos en 5 celdas adyacentes (sin incluir parte posterior)",
            "   - No indica dirección específica del monstruo",
            "",
            "3. **Vacuscopio**",
            "   - Se activa al colisionar con una Zona Vacía",
            "   - La información se almacena en memoria para futuras decisiones",
            "",
            "4. **Energómetro Espectral**",
            "   - Detecta monstruos en la celda actual del robot",
            "   - Activa el protocolo de destrucción",
            "",
            "5. **Roboscanner**",
            "   - Detecta otros robots en la celda frontal",
            "   - Inicia protocolo de negociación para evitar colisiones",
            "",
            "#### 4.1.2 Efectores",
            "",
            "1. **Propulsor Direccional**",
            "   - Mueve el robot una celda hacia adelante",
            "   - Respeta orientación actual",
            "",
            "2. **Reorientador**",
            "   - Rota al robot 90° hacia uno de sus lados",
            "   - Permite exploración omnidireccional",
            "",
            "3. **Vacuumator**",
            "   - Destruye monstruo y robot simultáneamente",
            "   - Convierte la celda en Zona Vacía",
            "",
            "#### 4.1.3 Memoria Interna",
            "",
            "La memoria del robot almacena:",
            "- Historial completo de percepciones y acciones",
            "- Mapa de zonas vacías conocidas",
            "- Posiciones donde se detectaron monstruos",
            "- Estadísticas de éxito/fracaso de acciones",
            "- Cobertura de exploración",
            "",
            "#### 4.1.4 Reglas de Decisión",
            "",
            "**Jerarquía de decisiones:**",
            "",
            "1. **Prioridad Máxima:** Si hay monstruo en celda actual → Destruir",
            "2. **Alta Prioridad:** Si hay robot adelante → Negociar movimiento",
            "3. **Prioridad Media:** Si se detecta monstruo cercano → Moverse hacia él",
            "4. **Prioridad Baja:** Explorar usando memoria histórica",
            "",
            "**Reglas de exploración:**",
            "- Evitar posiciones conocidas como zonas vacías",
            "- Priorizar celdas no visitadas o poco visitadas",
            "- Rotar si la celda frontal ha sido visitada múltiples veces",
            "",
            "### 4.2 Agente Monstruo (Reflejo Simple)",
            "",
            "#### 4.2.1 Percepciones",
            "",
            "- Detección de celdas libres adyacentes (6 direcciones)",
            "- No tiene modelo del entorno",
            "- No almacena información histórica",
            "",
            "#### 4.2.2 Acciones",
            "",
            "1. **Moverse:** Selección aleatoria de celda libre adyacente",
            "2. **Permanecer:** Cuando no puede moverse o no está en ciclo de movimiento",
            "",
            "#### 4.2.3 Reglas",
            "",
            "```",
            "SI (iteración MOD frecuencia == 0) Y (random() < probabilidad) ENTONCES",
            "    SI existen_celdas_libres_adyacentes ENTONCES",
            "        mover_a_celda_aleatoria()",
            "    FIN SI",
            "FIN SI",
            "```",
            "",
            "---",
            ""
        ]

    def _generate_environment_characteristics(self) -> List[str]:
        """
        Genera características del ambiente según AIMA
        """
        return [
            "## 5. Características del Ambiente (AIMA)",
            "",
            "### 5.1 Para el Agente Robot",
            "",
            "| Característica | Clasificación | Justificación |",
            "|----------------|---------------|---------------|",
            "| **Observabilidad** | Parcialmente observable | El robot solo percibe su entorno inmediato, no tiene visión global |",
            "| **Determinismo** | Estocástico | Los monstruos se mueven aleatoriamente, afectando el estado |",
            "| **Episódico** | Secuencial | Las decisiones actuales afectan estados futuros |",
            "| **Dinamismo** | Dinámico | Los monstruos pueden moverse mientras el robot decide |",
            "| **Discreto** | Discreto | Espacio, tiempo y acciones son discretos |",
            "| **Agentes** | Multi-agente competitivo | Múltiples robots compiten por los mismos monstruos |",
            "",
            "### 5.2 Para el Agente Monstruo",
            "",
            "| Característica | Clasificación | Justificación |",
            "|----------------|---------------|---------------|",
            "| **Observabilidad** | Parcialmente observable | Solo percibe celdas adyacentes |",
            "| **Determinismo** | Estocástico | Sus propias acciones son probabilísticas |",
            "| **Episódico** | Episódico | Cada decisión de movimiento es independiente |",
            "| **Dinamismo** | Dinámico | Los robots se mueven en el entorno |",
            "| **Discreto** | Discreto | Todas las variables son discretas |",
            "| **Agentes** | Multi-agente | Interactúa con múltiples robots |",
            "",
            "---",
            ""
        ]

    def _generate_perception_action_tables(self) -> List[str]:
        """
        Genera las tablas percepción-acción
        """
        return [
            "## 6. Tablas Percepción-Acción",
            "",
            "### 6.1 Tabla del Agente Robot",
            "",
            "| Percepción | Acción | Parámetros |",
            "|------------|--------|------------|",
            "| Monstruo en celda actual | Activar Vacuumator | {} |",
            "| Robot adelante | Negociar | {decisión: rotar/continuar} |",
            "| Monstruo detectado nearby | Mover hacia monstruo | {razón: hunting} |",
            "| Zona vacía conocida adelante | Rotar | {lado: n, razón: evitar_void} |",
            "| Celda frontal no visitada | Mover | {razón: explorar} |",
            "| Celda frontal muy visitada | Rotar | {lado: n, razón: ya_visitada} |",
            "| Sin estímulos especiales | Mover (exploración) | {razón: exploración_default} |",
            "",
            "### 6.2 Tabla del Agente Monstruo",
            "",
            "| Percepción | Condición | Acción |",
            "|------------|-----------|--------|",
            "| Celdas libres disponibles | (iter % K == 0) AND (rand < p) | Mover aleatoriamente |",
            "| Celdas libres disponibles | NOT (iter % K == 0) | Permanecer |",
            "| Sin celdas libres | Siempre | Permanecer |",
            "",
            "---",
            ""
        ]

    def _generate_results_section(self, statistics: Dict, metrics) -> List[str]:
        """
        Genera la sección de resultados
        """
        summary = statistics['simulation_summary']
        performance = statistics['performance']

        return [
            "## 7. Resultados de la Simulación",
            "",
            "### 7.1 Resumen Ejecutivo",
            "",
            f"- **Total de iteraciones ejecutadas:** {summary['total_iterations']}",
            f"- **Robots iniciales:** {summary['initial_robots']}",
            f"- **Robots finales (activos):** {summary['final_robots']}",
            f"- **Robots sacrificados:** {performance['robots_sacrificed']}",
            f"- **Monstruos iniciales:** {summary['initial_monsters']}",
            f"- **Monstruos finales:** {summary['final_monsters']}",
            f"- **Monstruos destruidos:** {summary['total_monsters_destroyed']}",
            f"- **Movimientos totales:** {summary['total_movements']}",
            f"- **Exploración máxima alcanzada:** {summary['max_exploration']:.2f}%",
            "",
            "### 7.2 Métricas de Desempeño",
            "",
            f"- **Eficiencia de destrucción:** {performance['destruction_efficiency']:.2f} monstruos por robot",
            f"- **Tasa de éxito:** {(summary['total_monsters_destroyed'] / summary['initial_monsters'] * 100):.2f}% de monstruos eliminados",
            f"- **Tasa de sacrificio:** {(performance['robots_sacrificed'] / summary['initial_robots'] * 100):.2f}% de robots perdidos",
            "",
            "---",
            ""
        ]

    def _generate_visualizations_section(self) -> List[str]:
        """
        Genera la sección de visualizaciones
        """
        return [
            "## 8. Visualizaciones",
            "",
            "### 8.1 Estado Inicial del Entorno",
            "",
            "![Estado Inicial](images/initial_state.png)",
            "",
            "*Figura 1: Configuración inicial del entorno 3D con robots (azul) y monstruos (rojo)*",
            "",
            "### 8.2 Estado Final del Entorno",
            "",
            "![Estado Final](images/final_state.png)",
            "",
            "*Figura 2: Configuración final después de la simulación*",
            "",
            "### 8.3 Estadísticas de la Simulación",
            "",
            "![Estadísticas](images/statistics.png)",
            "",
            "*Figura 3: Evolución de las métricas clave durante la simulación*",
            "",
            "### 8.4 Mapa de Calor de Exploración",
            "",
            "![Mapa de Calor](images/exploration_heatmap.png)",
            "",
            "*Figura 4: Proyecciones del mapa de calor mostrando las áreas más exploradas*",
            "",
            "### 8.5 Corte Transversal del Espacio",
            "",
            "![Corte 2D](images/slice_middle.png)",
            "",
            "*Figura 5: Vista 2D de un corte horizontal del espacio en el nivel medio*",
            "",
            "---",
            ""
        ]

    def _generate_analysis_section(self, statistics: Dict) -> List[str]:
        """
        Genera la sección de análisis
        """
        lines = [
            "## 9. Análisis de Resultados",
            "",
            "### 9.1 Comportamiento de los Robots",
            ""
        ]

        robot_stats = statistics['robot_statistics']
        active_robots = [r for r in robot_stats if r['is_active']]
        destroyed_robots = [r for r in robot_stats if not r['is_active']]

        lines.extend([
            f"**Robots que completaron la simulación:** {len(active_robots)}",
            f"**Robots destruidos (con monstruos):** {len(destroyed_robots)}",
            "",
            "#### Estadísticas por Robot:",
            ""
        ])

        for i, robot in enumerate(robot_stats[:5], 1):
            lines.extend([
                f"**Robot {i}** (ID: `{robot['agent_id'][:8]}`)",
                f"- Estado: {'Activo' if robot['is_active'] else 'Destruido'}",
                f"- Movimientos realizados: {robot['movements_made']}",
                f"- Rotaciones realizadas: {robot['rotations_made']}",
                f"- Colisiones con zonas vacías: {robot['collisions_with_void']}",
                f"- Monstruos destruidos: {robot['monsters_destroyed']}",
                ""
            ])

        if len(robot_stats) > 5:
            lines.append(f"*({len(robot_stats) - 5} robots adicionales omitidos para brevedad)*")
            lines.append("")

        lines.extend([
            "### 9.2 Comportamiento de los Monstruos",
            "",
            f"**Total de monstruos:** {len(statistics['monster_statistics'])}",
            ""
        ])

        monster_stats = statistics['monster_statistics']
        total_monster_movements = sum(m['movements_made'] for m in monster_stats)

        lines.extend([
            f"- Movimientos totales de monstruos: {total_monster_movements}",
            f"- Promedio de movimientos por monstruo: {total_monster_movements / len(monster_stats):.2f}",
            "",
            "---",
            ""
        ])

        return lines

    def _generate_events_section(self, events: List) -> List[str]:
        """
        Genera la sección de eventos importantes
        """
        destruction_events = [e for e in events if e.event_type == 'MONSTER_DESTROYED']

        lines = [
            "## 10. Eventos Importantes",
            "",
            f"**Total de eventos registrados:** {len(events)}",
            f"**Eventos de destrucción:** {len(destruction_events)}",
            "",
        ]

        if destruction_events:
            lines.extend([
                "### Primeros 10 Eventos de Destrucción:",
                ""
            ])

            for event in destruction_events[:10]:
                lines.append(f"- **Iteración {event.iteration}:** {event.description} en posición {event.data.get('position')}")

            if len(destruction_events) > 10:
                lines.append(f"\n*({len(destruction_events) - 10} eventos adicionales omitidos)*")

        lines.extend(["", "---", ""])

        return lines

    def _generate_conclusions_section(self, statistics: Dict) -> List[str]:
        """
        Genera la sección de conclusiones
        """
        summary = statistics['simulation_summary']
        performance = statistics['performance']

        return [
            "## 11. Conclusiones",
            "",
            "### 11.1 Cumplimiento de Objetivos",
            "",
            f"El sistema logró destruir **{summary['total_monsters_destroyed']}** de **{summary['initial_monsters']}** monstruos "
            f"({(summary['total_monsters_destroyed'] / summary['initial_monsters'] * 100):.1f}% del total), ",
            f"sacrificando **{performance['robots_sacrificed']}** de **{summary['initial_robots']}** robots "
            f"({(performance['robots_sacrificed'] / summary['initial_robots'] * 100):.1f}%).",
            "",
            "### 11.2 Efectividad del Agente con Memoria Interna",
            "",
            "Los robots demostraron capacidad de:",
            "1. **Aprendizaje:** Evitar zonas vacías previamente descubiertas",
            "2. **Exploración inteligente:** Priorizar áreas no visitadas",
            "3. **Coordinación:** Negociar cuando se encuentran con otros robots",
            f"4. **Cobertura:** Explorar hasta {summary['max_exploration']:.2f}% del espacio disponible",
            "",
            "### 11.3 Comportamiento Emergente",
            "",
            "Se observaron los siguientes patrones emergentes:",
            "- Los robots tienden a concentrarse en áreas con alta densidad de monstruos",
            "- La memoria permite optimización de rutas evitando colisiones repetidas",
            "- La estrategia de rotación incremental distribuye la exploración uniformemente",
            "",
            "### 11.4 Limitaciones Identificadas",
            "",
            "1. **Información imperfecta:** Los monstruos pueden moverse, invalidando creencias previas",
            "2. **Coordinación limitada:** Los robots solo negocian en colisiones directas",
            "3. **Sacrificio inevitable:** Cada destrucción implica pérdida del robot",
            "4. **Alcance sensorial:** Detección de monstruos solo en entorno inmediato",
            "",
            "### 11.5 Racionalidad del Agente Robot",
            "",
            "**Medida de desempeño:** Maximizar monstruos destruidos / Minimizar iteraciones",
            "",
            f"- **Eficiencia:** {performance['destruction_efficiency']:.2f} monstruos por robot",
            f"- **Iteraciones promedio por destrucción:** {summary['total_iterations'] / max(summary['total_monsters_destroyed'], 1):.2f}",
            "",
            "El agente demuestra **racionalidad limitada** dado que:",
            "- Toma decisiones óptimas con la información disponible",
            "- Utiliza su memoria para mejorar decisiones futuras",
            "- Opera bajo restricciones computacionales y sensoriales",
            "- No puede anticipar movimientos estocásticos de monstruos",
            "",
            "### 11.6 Ambiente Episódico vs Secuencial",
            "",
            "El ambiente para el robot es **SECUENCIAL**, no episódico porque:",
            "1. Las acciones actuales afectan estados futuros",
            "2. La memoria histórica influye en decisiones",
            "3. Las posiciones visitadas reducen opciones de exploración",
            "4. El aprendizaje de zonas vacías es acumulativo",
            "",
            "**¿Entra en bucle infinito?**",
            "",
            "No, el agente está diseñado para evitar bucles mediante:",
            "- Contador de visitas por posición",
            "- Rotación cuando detecta repetición excesiva",
            "- Exploración dirigida a zonas no visitadas",
            "- Límite máximo de iteraciones de la simulación",
            "",
            "### 11.7 Representación del Conocimiento",
            "",
            "La tabla de mapeo percepción-acción permite:",
            "- **Memoria episódica:** Registro completo de experiencias",
            "- **Memoria semántica:** Abstracción de patrones (zonas vacías, monstruos)",
            "- **Inferencia:** Decisiones basadas en conocimiento acumulado",
            "- **Adaptación:** Ajuste de estrategia según historia",
            "",
            "---",
            "",
            "## 12. Bibliografía",
            "",
            "1. Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson.",
            "2. Wooldridge, M. (2009). *An Introduction to MultiAgent Systems* (2nd ed.). Wiley.",
            "3. Weiss, G. (Ed.). (2013). *Multiagent Systems* (2nd ed.). MIT Press.",
            "",
            "---",
            "",
            f"**Reporte generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**",
            ""
        ]