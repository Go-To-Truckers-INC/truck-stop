from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Type
from dataclasses import dataclass


@dataclass
class Route:
    """Modelo para representar una ruta"""
    rule: str
    endpoint: str
    view_func: Callable
    methods: List[str]
    options: Dict[str, Any]


@dataclass
class Blueprint:
    """Modelo para representar un blueprint"""
    name: str
    blueprint: Any
    url_prefix: str
    options: Dict[str, Any]


@dataclass
class ErrorHandler:
    """Modelo para representar un manejador de errores"""
    code: int
    handler: Callable


@dataclass
class Middleware:
    """Modelo para representar middleware"""
    name: str
    middleware_func: Callable
    middleware_type: str  # 'before_request', 'after_request', 'teardown_request'


class Server(ABC):
    """
    Clase abstracta para modelar un servidor Flask robusto y completo
    Sin dependencias ocultas - toda la configuración es explícita
    """

    @abstractmethod
    def __init__(self, name: str):
        """
        Inicializa el servidor

        Args:
            name: Nombre de la aplicación
        """
        self.name: str = name
        self.host: str = '0.0.0.0'
        self.port: int = 5000
        self.debug: bool = False
        self.environment: str = 'production'

        # Configuración explícita
        self.config: Dict[str, Any] = {}
        self.routes: List[Route] = []
        self.blueprints: List[Blueprint] = []
        self.error_handlers: List[ErrorHandler] = []
        self.middlewares: List[Middleware] = []
        self.extensions: Dict[str, Any] = {}

        self._initialized: bool = False

    @abstractmethod
    def initialize(self) -> bool:
        """
        Inicializa el servidor con configuración básica

        Returns:
            bool: True si la inicialización fue exitosa
        """
        pass

    @abstractmethod
    def set_config(self, config: Dict[str, Any]) -> None:
        """
        Establece la configuración del servidor

        Args:
            config: Diccionario con configuración
        """
        pass

    @abstractmethod
    def add_route(self, rule: str, view_func: Callable,
                  endpoint: Optional[str] = None,
                  methods: List[str] = None,
                  **options: Any) -> None:
        """
        Agrega una ruta al servidor

        Args:
            rule: Ruta URL
            view_func: Función de vista
            endpoint: Nombre del endpoint (opcional)
            methods: Métodos HTTP permitidos
            **options: Opciones adicionales
        """
        pass

    @abstractmethod
    def add_blueprint(self, blueprint: Any,
                      url_prefix: str = None,
                      **options: Any) -> None:
        """
        Registra un blueprint en el servidor

        Args:
            blueprint: Blueprint a registrar
            url_prefix: Prefijo de URL
            **options: Opciones adicionales
        """
        pass

    @abstractmethod
    def add_error_handler(self, code: int, handler: Callable) -> None:
        """
        Registra un manejador de errores

        Args:
            code: Código de error HTTP
            handler: Función manejadora
        """
        pass

    @abstractmethod
    def add_middleware(self, middleware_func: Callable,
                       middleware_type: str = 'before_request',
                       name: str = None) -> None:
        """
        Agrega middleware al servidor

        Args:
            middleware_func: Función middleware
            middleware_type: Tipo de middleware
            name: Nombre identificador
        """
        pass

    @abstractmethod
    def add_extension(self, name: str, extension: Any) -> None:
        """
        Agrega una extensión al servidor

        Args:
            name: Nombre de la extensión
            extension: Instancia de la extensión
        """
        pass

    @abstractmethod
    def get_extension(self, name: str) -> Any:
        """
        Obtiene una extensión por nombre

        Args:
            name: Nombre de la extensión

        Returns:
            Any: Extensión o None si no existe
        """
        pass

    @abstractmethod
    def setup_cors(self, origins: List[str] = None,
                   methods: List[str] = None,
                   allow_headers: List[str] = None) -> None:
        """
        Configura CORS para el servidor

        Args:
            origins: Lista de orígenes permitidos
            methods: Métodos HTTP permitidos
            allow_headers: Headers permitidos
        """
        pass

    @abstractmethod
    def setup_json_encoding(self) -> None:
        """
        Configura la codificación JSON personalizada
        """
        pass

    @abstractmethod
    def setup_logging(self) -> None:
        """
        Configura el sistema de logging
        """
        pass

    @abstractmethod
    def setup_security_headers(self) -> None:
        """
        Configura headers de seguridad
        """
        pass

    @abstractmethod
    def create_app(self) -> Any:
        """
        Crea la instancia de la aplicación Flask

        Returns:
            Any: Instancia de Flask
        """
        pass

    @abstractmethod
    def get_app(self) -> Any:
        """
        Obtiene la instancia de la aplicación

        Returns:
            Any: Instancia de Flask
        """
        pass

    @abstractmethod
    def run(self, host: str = None, port: int = None,
            debug: bool = None, **options: Any) -> None:
        """
        Ejecuta el servidor

        Args:
            host: Host del servidor
            port: Puerto del servidor
            debug: Modo debug
            **options: Opciones adicionales
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """
        Apaga el servidor y limpia todos los recursos
        """
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del servidor

        Returns:
            Dict[str, Any]: Estado del servidor
        """
        pass

    @abstractmethod
    def is_initialized(self) -> bool:
        """
        Verifica si el servidor está inicializado

        Returns:
            bool: True si está inicializado
        """
        pass

    @abstractmethod
    def reload(self) -> bool:
        """
        Recarga la configuración del servidor

        Returns:
            bool: True si la recarga fue exitosa
        """
        pass