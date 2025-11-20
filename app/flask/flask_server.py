import os
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from flask import Flask, jsonify, request, Response
from flask_cors import CORS

from ..core.server import Server, Route, Blueprint, ErrorHandler, Middleware


class FlaskServer(Server):
    """
    Implementación concreta y completa de un servidor Flask robusto
    Sin dependencias ocultas - toda la configuración es explícita y transparente
    """

    def __init__(self, name: str = __name__):
        super().__init__(name)
        self.app: Optional[Flask] = None
        self.logger: Optional[logging.Logger] = None

        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.template_folder = os.path.join(current_dir, '..', 'templates')
        self.static_folder = os.path.join(current_dir, '..', 'public')

        # Configuración por defecto explícita
        self.default_config = {
            'SECRET_KEY': 'dev-secret-key-change-in-production',
            'DEBUG': False,
            'TESTING': False,
            'ENV': 'production',
            'JSON_SORT_KEYS': False,
            'JSONIFY_PRETTYPRINT_REGULAR': False,
            'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
        }

    def initialize(self) -> bool:
        """
        Inicialización completa y explícita del servidor
        """
        try:
            if self._initialized:
                return True

            # 1. Crear aplicación Flask
            self.app = Flask(
                self.name,
                template_folder=self.template_folder,
                static_folder=self.static_folder
            )

            # 2. Configurar logging
            self.setup_logging()

            # 3. Aplicar configuración por defecto
            self.set_config(self.default_config)

            # 4. Configuraciones básicas
            self.setup_json_encoding()
            self.setup_security_headers()

            # 5. Configurar CORS por defecto
            self.setup_cors()

            # 6. Configurar rutas de sistema
            self._setup_system_routes()

            # 7. Configurar manejadores de error por defecto
            self._setup_default_error_handlers()

            # 8. Configurar middleware de logging
            self._setup_logging_middleware()

            self._initialized = True
            self.logger.info("✅ Flask server inicializado correctamente")
            return True

        except Exception as e:
            print(f"❌ Error inicializando Flask server: {e}")
            self._initialized = False
            return False

    def set_config(self, config: Dict[str, Any]) -> None:
        """Establece configuración explícita"""
        if not self.app:
            raise RuntimeError("Server no inicializado")

        self.config.update(config)
        self.app.config.update(config)

        # Actualizar propiedades derivadas
        self.debug = config.get('DEBUG', False)
        self.environment = config.get('ENV', 'production')

    def add_route(self, rule: str, view_func: Callable,
                  endpoint: Optional[str] = None,
                  methods: List[str] = None,
                  **options: Any) -> None:
        """Agrega ruta de forma explícita"""
        if not self.app:
            raise RuntimeError("Server no inicializado")

        if methods is None:
            methods = ['GET']

        if endpoint is None:
            endpoint = view_func.__name__

        # Crear y almacenar ruta
        route = Route(
            rule=rule,
            endpoint=endpoint,
            view_func=view_func,
            methods=methods,
            options=options
        )
        self.routes.append(route)

        # Registrar en Flask
        self.app.add_url_rule(rule, endpoint, view_func, methods=methods, **options)

        self.logger.debug(f"📌 Ruta registrada: {rule} -> {endpoint}")

    def add_blueprint(self, blueprint: Any,
                      url_prefix: str = None,
                      **options: Any) -> None:
        """Registra blueprint de forma explícita"""
        if not self.app:
            raise RuntimeError("Server no inicializado")

        # Crear y almacenar blueprint
        bp = Blueprint(
            name=blueprint.name,
            blueprint=blueprint,
            url_prefix=url_prefix,
            options=options
        )
        self.blueprints.append(bp)

        # Registrar en Flask
        self.app.register_blueprint(blueprint, url_prefix=url_prefix, **options)

        self.logger.debug(f"📦 Blueprint registrado: {blueprint.name}")

    def add_error_handler(self, code: int, handler: Callable) -> None:
        """Registra manejador de errores explícito"""
        if not self.app:
            raise RuntimeError("Server no inicializado")

        # Crear y almacenar error handler
        error_handler = ErrorHandler(code=code, handler=handler)
        self.error_handlers.append(error_handler)

        # Registrar en Flask
        self.app.errorhandler(code)(handler)

        self.logger.debug(f"🛡️ Manejador de error registrado: HTTP {code}")

    def add_middleware(self, middleware_func: Callable,
                       middleware_type: str = 'before_request',
                       name: str = None) -> None:
        """Agrega middleware explícito"""
        if not self.app:
            raise RuntimeError("Server no inicializado")

        if name is None:
            name = middleware_func.__name__

        # Crear y almacenar middleware
        middleware = Middleware(
            name=name,
            middleware_func=middleware_func,
            middleware_type=middleware_type
        )
        self.middlewares.append(middleware)

        # Registrar en Flask según el tipo
        if middleware_type == 'before_request':
            self.app.before_request(middleware_func)
        elif middleware_type == 'after_request':
            self.app.after_request(middleware_func)
        elif middleware_type == 'teardown_request':
            self.app.teardown_request(middleware_func)
        else:
            raise ValueError(f"Tipo de middleware no válido: {middleware_type}")

        self.logger.debug(f"🔧 Middleware registrado: {name} ({middleware_type})")

    def add_extension(self, name: str, extension: Any) -> None:
        """Agrega extensión explícita"""
        self.extensions[name] = extension
        self.logger.debug(f"🔌 Extensión registrada: {name}")

    def get_extension(self, name: str) -> Any:
        """Obtiene extensión por nombre"""
        return self.extensions.get(name)

    def setup_cors(self, origins: List[str] = None,
                   methods: List[str] = None,
                   allow_headers: List[str] = None) -> None:
        """Configura CORS explícitamente"""
        if not self.app:
            raise RuntimeError("Server no inicializado")

        if origins is None:
            origins = ['*']

        if methods is None:
            methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']

        if allow_headers is None:
            allow_headers = ['Content-Type', 'Authorization']

        # Registrar CORS como extensión
        cors = CORS(self.app, resources={
            r"/api/*": {
                "origins": origins,
                "methods": methods,
                "allow_headers": allow_headers
            }
        })

        self.add_extension('cors', cors)
        self.logger.info("🌐 CORS configurado")

    def setup_json_encoding(self) -> None:
        """Configura codificación JSON personalizada"""

        class CustomJSONEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)

        if self.app:
            self.app.json_encoder = CustomJSONEncoder

    def setup_logging(self) -> None:
        """Configura sistema de logging explícito"""
        self.logger = logging.getLogger(self.name)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def setup_security_headers(self) -> None:
        """Configura headers de seguridad explícitos"""

        @self.app.after_request
        def set_security_headers(response):
            # Headers básicos de seguridad
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'

            # CSP básico
            if self.environment == 'production':
                response.headers['Content-Security-Policy'] = "default-src 'self'"

            return response

        self.logger.debug("🔒 Headers de seguridad configurados")

    def create_app(self) -> Any:
        """Crea la aplicación Flask"""
        return self.app

    def get_app(self) -> Any:
        """Obtiene la aplicación Flask"""
        if not self.app:
            raise RuntimeError("Server no inicializado")
        return self.app

    def run(self, host: str = None, port: int = None,
            debug: bool = None, **options: Any) -> None:
        """Ejecuta el servidor de forma explícita"""
        if not self.app:
            raise RuntimeError("Server no inicializado")

        # Usar valores proporcionados o los de configuración
        run_host = host or self.host
        run_port = port or self.port
        run_debug = debug if debug is not None else self.debug

        # Configuración de ejecución
        run_options = {
            'host': run_host,
            'port': run_port,
            'debug': run_debug,
            'use_reloader': run_debug,
            'threaded': True
        }
        run_options.update(options)

        self.logger.info(f"🚀 Iniciando servidor en {run_host}:{run_port} "
                         f"(debug: {run_debug}, env: {self.environment})")

        self.app.run(**run_options)

    def shutdown(self) -> None:
        """Apaga el servidor y limpia todo explícitamente"""
        self.logger.info("🛑 Apagando servidor...")

        # Limpiar todas las listas
        self.routes.clear()
        self.blueprints.clear()
        self.error_handlers.clear()
        self.middlewares.clear()
        self.extensions.clear()
        self.config.clear()

        self.app = None
        self._initialized = False

        self.logger.info("✅ Servidor apagado correctamente")

    def get_status(self) -> Dict[str, Any]:
        """Obtiene estado completo del servidor"""
        return {
            'initialized': self._initialized,
            'name': self.name,
            'environment': self.environment,
            'debug': self.debug,
            'host': self.host,
            'port': self.port,
            'routes_count': len(self.routes),
            'blueprints_count': len(self.blueprints),
            'error_handlers_count': len(self.error_handlers),
            'middlewares_count': len(self.middlewares),
            'extensions_count': len(self.extensions),
            'config_keys': list(self.config.keys())
        }

    def is_initialized(self) -> bool:
        return self._initialized

    def reload(self) -> bool:
        """Recarga la configuración del servidor"""
        self.logger.info("🔄 Recargando configuración del servidor...")

        try:
            # Backup de configuración actual
            current_config = self.config.copy()
            current_routes = self.routes.copy()

            # Reinicializar
            self.shutdown()

            # Recrear con configuración anterior
            if self.initialize():
                self.set_config(current_config)

                # Re-registrar rutas
                for route in current_routes:
                    self.add_route(
                        rule=route.rule,
                        view_func=route.view_func,
                        endpoint=route.endpoint,
                        methods=route.methods,
                        **route.options
                    )

                self.logger.info("✅ Configuración recargada correctamente")
                return True
            else:
                return False

        except Exception as e:
            self.logger.error(f"❌ Error recargando configuración: {e}")
            return False

    def _setup_system_routes(self) -> None:
        """Configura rutas del sistema"""

        @self.app.route('/health')
        def health():
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'server': self.get_status()
            })

        @self.app.route('/status')
        def status():
            return jsonify(self.get_status())

    def _setup_default_error_handlers(self) -> None:
        """Configura manejadores de error por defecto"""

        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                'error': 'Recurso no encontrado',
                'message': str(error),
                'path': request.path,
                'timestamp': datetime.now().isoformat()
            }), 404

        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({
                'error': 'Error interno del servidor',
                'message': 'Ocurrió un error inesperado',
                'timestamp': datetime.now().isoformat()
            }), 500

        @self.app.errorhandler(400)
        def bad_request(error):
            return jsonify({
                'error': 'Solicitud incorrecta',
                'message': str(error),
                'timestamp': datetime.now().isoformat()
            }), 400

        @self.app.errorhandler(405)
        def method_not_allowed(error):
            return jsonify({
                'error': 'Método no permitido',
                'message': str(error),
                'timestamp': datetime.now().isoformat()
            }), 405

    def _setup_logging_middleware(self) -> None:
        """Configura middleware de logging"""

        @self.app.before_request
        def log_request():
            self.logger.info(f"📥 {request.method} {request.path} - "
                             f"IP: {request.remote_addr} - "
                             f"User-Agent: {request.user_agent}")

        @self.app.after_request
        def log_response(response):
            self.logger.info(f"📤 {request.method} {request.path} - "
                             f"Status: {response.status_code}")
            return response