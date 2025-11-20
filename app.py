import os

from dotenv import load_dotenv
from flask_talisman import Talisman

# Cargar variables de entorno AL INICIO
load_dotenv()

from app.flask.flask_server import FlaskServer
from app.core.sdk_manager import SDKManager

# Importar blueprints
from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.companies import companies_bp
from app.routes.developers import developers_bp


def setup_sdks():
    """Configura y inicializa todos los SDKs con manejo graceful de errores"""
    sdk_manager = SDKManager()

    try:
        pass
        # # Configuración explícita de Firebase SDK
        # firebase_sdk = FirebaseSDK()
        #
        # # Intentar inicializar Firebase
        # firebase_initialized = firebase_sdk.initialize()
        #
        # if firebase_initialized:
        #     print("✅ Firebase SDK inicializado correctamente")
        # else:
        #     error_msg = firebase_sdk.get_error() or "Error desconocido"
        #     print(f"⚠️  Firebase SDK no se pudo inicializar: {error_msg}")
        #     print("⚠️  La aplicación continuará sin funcionalidades de Firebase")
        #
        # # Registrar el SDK independientemente del resultado
        # registration_success = sdk_manager.register_sdk('firebase', firebase_sdk)
        #
        # if not registration_success:
        #     print("❌ Error registrando Firebase SDK en el manager")

    except Exception as e:
        print(f"❌ Error inesperado configurando SDKs: {e}")
        print("⚠️  La aplicación continuará sin SDKs adicionales")

    return sdk_manager

def create_app():
    """Factory function para crear la aplicación Flask"""
    # 1. Configurar SDKs
    sdk_manager = setup_sdks()

    # 2. Crear servidor
    server = FlaskServer('truck_stop_app')

    csp = {
        "default-src": ["'self'"],
        "style-src": [
            "'self'",
            "https://cdn.jsdelivr.net",
            "'unsafe-inline'"  # Necesario para Bootstrap y estilos inline
        ],
        "script-src": [
            "'self'",
            "https://cdn.jsdelivr.net",
            "'unsafe-inline'"  # Necesario para scripts inline de Bootstrap
        ],
        "font-src": [
            "'self'",
            "https://cdn.jsdelivr.net",
            "https://fonts.gstatic.com",
            "data:"
        ],
        "img-src": [
            "'self'",
            "data:",
            "https:",
            "blob:"
        ],
        "connect-src": ["'self'"],
        "frame-src": ["'none'"],
        "object-src": ["'none'"],
        "base-uri": ["'self'"]
    }

    # Inicializa Talisman
    Talisman(
        server.app,
        content_security_policy=csp,
        content_security_policy_nonce_in=['script-src', 'style-src'],
        force_https=False
    )

    # 3. Configuración
    config = {
        'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
        'DEBUG': os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        'ENV': os.getenv('FLASK_ENV', 'production'),
        'TESTING': os.getenv('TESTING', 'False').lower() == 'true',
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,
        'JSON_SORT_KEYS': False,
    }

    # 4. Inicializar servidor
    if not server.initialize():
        raise RuntimeError("❌ Error inicializando el servidor Flask")

    # 5. Aplicar configuración
    server.set_config(config)

    # 6. Configurar CORS
    allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')

    server.setup_cors(
        origins=allowed_origins,
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
        allow_headers=['Content-Type', 'Authorization', 'X-Requested-With']
    )

    # 7. Registrar blueprints
    server.add_blueprint(main_bp)
    server.add_blueprint(auth_bp)
    server.add_blueprint(dashboard_bp)
    server.add_blueprint(companies_bp)
    server.add_blueprint(developers_bp)

    # 8. Configurar rutas del sistema
    def setup_system_routes():
        @server.app.route('/api/status')
        def api_status():
            sdk_status = sdk_manager.get_status() if sdk_manager else {}
            return {
                'status': 'operational',
                'server': server.get_status(),
                'sdks': sdk_status,
                'timestamp': os.getenv('BUILD_TIMESTAMP', 'unknown')
            }

        @server.app.route('/api/health')
        def health_check():
            return {
                'status': 'healthy',
                'server': 'running',
                'sdks_initialized': sdk_manager.get_all_initialized() if sdk_manager else []
            }

    setup_system_routes()

    print("✅ Servidor Flask configurado correctamente")
    return server.app


# Esta es la variable que Gunicorn busca
application = create_app()

if __name__ == "__main__":
    # Solo para desarrollo local
    app = create_app()
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    app.run(host=host, port=port, debug=debug)