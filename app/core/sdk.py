from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class SDK(ABC):
    """
    Clase abstracta para la inicialización de SDKs de servicios externos
    como Firebase, AWS, Google Cloud, etc.
    """

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Inicializa el SDK con la configuración proporcionada

        Args:
            config: Diccionario con la configuración necesaria

        Returns:
            bool: True si la inicialización fue exitosa, False en caso contrario
        """
        pass

    @abstractmethod
    def is_initialized(self) -> bool:
        """
        Verifica si el SDK está inicializado

        Returns:
            bool: True si está inicializado, False en caso contrario
        """
        pass

    @abstractmethod
    def get_client(self) -> Any:
        """
        Retorna el cliente del SDK inicializado

        Returns:
            Any: Cliente del SDK o None si no está inicializado
        """
        pass

    @abstractmethod
    def cleanup(self) -> bool:
        """
        Limpieza de recursos del SDK

        Returns:
            bool: True si la limpieza fue exitosa
        """
        pass

    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """
        Retorna la configuración actual del SDK

        Returns:
            Dict[str, Any]: Configuración actual
        """
        pass