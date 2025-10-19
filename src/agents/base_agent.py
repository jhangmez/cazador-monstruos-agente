import abc
from typing import Dict, Any, Tuple
import uuid
from dataclasses import dataclass, field


@dataclass
class Action:
    """
    Representa una acción que un agente puede ejecutar.

    Atributos:
        action_type (str): El tipo de acción (e.g., 'move', 'rotate', 'destroy').
        parameters (Dict[str, Any]): Parámetros adicionales para la acción.
        success (bool): Indica si la acción se ejecutó con éxito. Se establece
                        después de la ejecución.
    """
    action_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    success: bool = False

    def __str__(self):
        return f"Action(type={self.action_type}, params={self.parameters}, success={self.success})"


@dataclass
class Perception:
    """
    Representa la percepción de un agente sobre el entorno en un momento dado.

    Atributos:
        timestamp (int): El número de iteración de la simulación.
        sensor_data (Dict[str, Any]): Los datos recopilados por los sensores del agente.
    """
    timestamp: int
    sensor_data: Dict[str, Any]

    def __str__(self):
        return f"Perception(t={self.timestamp}, data={self.sensor_data})"



class AgentState(abc.ABC):
    """
    Clase base abstracta para el estado interno de un agente.
    Mantiene la información que el agente recuerda entre iteraciones.
    """

    def __init__(self, agent_id: str):
        """
        Inicializa el estado del agente.

        Args:
            agent_id (str): El identificador único del agente.
        """
        self.agent_id: str = agent_id
        self.is_active: bool = True
        self.iteration_count: int = 0

    def is_active(self) -> bool:
        """Verifica si el agente está activo."""
        return self.is_active

    def deactivate(self):
        """Marca al agente como inactivo."""
        self.is_active = False

    @abc.abstractmethod
    def update(self, perception: Perception, action: Action):
        """
        Actualiza el estado interno del agente basado en la última percepción y acción.
        Este método debe ser implementado por las subclases.

        Args:
            perception (Perception): La percepción recibida.
            action (Action): La acción ejecutada.
        """
        pass


class BaseAgent(abc.ABC):
    """
    Clase base abstracta para todos los agentes en el sistema.
    Define la arquitectura PEAS (Perception, Environment, Actuators, Sensors)
    y el ciclo de operación principal: percibir -> decidir -> ejecutar.
    """

    def __init__(self, agent_id: str):
        """
        Inicializa un agente base.

        Args:
            agent_id (str): Un identificador legible para el agente (e.g., 'robot_1').
        """
        self._agent_id: str = f"{agent_id}_{uuid.uuid4().hex[:8]}"
        self.state: AgentState = self._initialize_state()

    @property
    def agent_id(self) -> str:
        """Retorna el identificador único del agente."""
        return self._agent_id

    @abc.abstractmethod
    def _initialize_state(self) -> AgentState:
        """
        Crea y retorna la instancia de estado específica para este tipo de agente.
        Debe ser implementado por las subclases.

        Returns:
            AgentState: Una subclase de AgentState (e.g., RobotState, MonsterState).
        """
        pass

    @abc.abstractmethod
    def perceive(self, environment: Any) -> Perception:
        """
        Utiliza los sensores del agente para percibir el entorno.
        Debe ser implementado por las subclases.

        Args:
            environment (Any): La instancia del entorno de simulación.

        Returns:
            Perception: Un objeto que contiene los datos sensoriales.
        """
        pass

    @abc.abstractmethod
    def decide(self, perception: Perception) -> Action:
        """
        Toma una decisión basada en la percepción actual y el estado interno (memoria).
        Debe ser implementado por las subclases.

        Args:
            perception (Perception): La percepción actual del agente.

        Returns:
            Action: La acción que el agente ha decidido ejecutar.
        """
        pass

    @abc.abstractmethod
    def execute(self, action: Action, environment: Any) -> bool:
        """
        Ejecuta una acción en el entorno utilizando sus efectores.
        Debe ser implementado por las subclases.

        Args:
            action (Action): La acción a ejecutar.
            environment (Any): La instancia del entorno de simulación.

        Returns:
            bool: True si la acción fue exitosa, False en caso contrario.
        """
        pass

    def operate(self, environment: Any) -> Tuple[Perception, Action, bool]:
        """
        Ejecuta un ciclo completo de operación del agente: percibir, decidir, actuar.
        Este es el método principal que el simulador llamará en cada iteración.

        Args:
            environment (Any): La instancia del entorno de simulación.

        Returns:
            Tuple[Perception, Action, bool]: La percepción, la acción ejecutada y el
                                             resultado de la ejecución. Retorna
                                             (None, None, False) si el agente está inactivo.
        """
        if not self.state.is_active:
            return None, None, False

        self.state.iteration_count += 1

        perception = self.perceive(environment)

        action = self.decide(perception)

        success = self.execute(action, environment)
        action.success = success

        self.state.update(perception, action)

        return perception, action, success

    def is_active(self) -> bool:
        """Verifica si el agente está activo a través de su estado."""
        return self.state.is_active

    def deactivate(self):
        """Desactiva el agente a través de su estado."""
        self.state.deactivate()

    @abc.abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna un diccionario con estadísticas de rendimiento del agente.
        Debe ser implementado por las subclases.

        Returns:
            Dict[str, Any]: Un diccionario con métricas relevantes del agente.
        """
        pass