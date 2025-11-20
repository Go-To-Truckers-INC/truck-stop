import os
from dotenv import load_dotenv
from flask_talisman import Talisman

# Cargar variables de entorno AL INICIO
load_dotenv()

from app.flask.flask_server import FlaskServer
from app.firebase.firebase_sdk import FirebaseSDK
from app.core.sdk_manager import SDKManager

# Importar blueprints
from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.companies import companies_bp
from app.routes.developers import developers_bp


def setup_sdks():
    """Configura y inicializa todos los SDKs de forma explícita"""
    sdk_manager = SDKManager()

    # Configuración explícita de Firebase SDK
    firebase_sdk = FirebaseSDK()

    if sdk_manager.register_sdk('firebase', firebase_sdk):
        print("✅ Firebase SDK inicializado correctamente")
    else:
        print("❌ Error inicializando Firebase SDK")

    return sdk_manager


def create_app():
    """Factory function para crear la aplicación Flask"""
    # 1. Configurar SDKs
    sdk_manager = setup_sdks()

    # 2. Crear servidor
    server = FlaskServer('truck_stop_app')

    csp = {
        "default-src": ["'self'"],
        "style-src": ["'self'", "https://cdn.jsdelivr.net", "'nonce-{{ g.nonce }}'"],
        "script-src": ["'self'", "https://cdn.jsdelivr.net", "'nonce-{{ g.nonce }}'"]
    }

    # Inicializa Talisman
    talisman = Talisman(server.app, content_security_policy=csp,
                        content_security_policy_nonce_in=['style-src', 'script-src'])

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
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    app.run(host=host, port=port, debug=debug)