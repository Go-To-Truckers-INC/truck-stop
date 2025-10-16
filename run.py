import os
from dotenv import load_dotenv

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


def setup_server(sdk_manager):
    """Configura y inicializa el servidor Flask con todas las rutas"""

    # 1. Crear servidor
    server = FlaskServer('truck_stop_app')

    # 2. Configuración explícita
    config = {
        'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
        'DEBUG': os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        'ENV': os.getenv('FLASK_ENV', 'production'),
        'TESTING': os.getenv('TESTING', 'False').lower() == 'true',
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,
        'JSON_SORT_KEYS': False,
    }

    # 3. Inicializar servidor
    if not server.initialize():
        print("❌ Error inicializando el servidor Flask")
        return None

    # 4. Aplicar configuración
    server.set_config(config)

    # 5. Configurar CORS
    allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
    server.setup_cors(
        origins=allowed_origins,
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
        allow_headers=['Content-Type', 'Authorization', 'X-Requested-With']
    )

    # 6. Registrar todos los blueprints
    server.add_blueprint(main_bp)
    server.add_blueprint(auth_bp)
    server.add_blueprint(dashboard_bp)
    server.add_blueprint(companies_bp)
    server.add_blueprint(developers_bp)

    # 7. Configurar rutas del sistema
    def setup_system_routes():
        """Configura rutas del sistema que integran con los SDKs"""

        @server.app.route('/api/status')
        def api_status():
            """Endpoint de estado que muestra información de SDKs"""
            sdk_status = sdk_manager.get_status() if sdk_manager else {}

            return {
                'status': 'operational',
                'server': server.get_status(),
                'sdks': sdk_status,
                'timestamp': os.getenv('BUILD_TIMESTAMP', 'unknown')
            }

        @server.app.route('/api/health')
        def health_check():
            """Health check que verifica estado de SDKs"""
            return {
                'status': 'healthy',
                'server': 'running',
                'sdks_initialized': sdk_manager.get_all_initialized() if sdk_manager else []
            }

    setup_system_routes()

    print("✅ Servidor Flask configurado correctamente con navegación completa")
    return server


def main():
    """Función principal"""
    print("🚀 Iniciando Truck Stop Application...")

    try:
        # 1. Configurar SDKs
        print("📦 Configurando SDKs...")
        sdk_manager = setup_sdks()

        # 2. Configurar servidor
        print("🔧 Configurando servidor Flask con navegación...")
        server = setup_server(sdk_manager)

        if not server:
            print("❌ No se pudo configurar el servidor. Saliendo.")
            return

        # 3. Mostrar rutas registradas
        print("\n🎯 RUTAS REGISTRADAS:")
        for route in server.app.url_map.iter_rules():
            if 'static' not in str(route):
                methods = ','.join(sorted(route.methods - {'OPTIONS', 'HEAD'}))
                print(f"   {methods:8} {route.rule:40} -> {route.endpoint}")

        # 4. Configuración de ejecución
        host = os.getenv('FLASK_HOST', '0.0.0.0')
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

        print(f"\n🌐 INICIANDO SERVICIO:")
        print(f"   Host: {host}")
        print(f"   Puerto: {port}")
        print(f"   Debug: {debug}")
        print(f"   Entorno: {os.getenv('FLASK_ENV', 'production')}")

        # 5. Ejecutar servidor
        print("\n" + "=" * 50)
        server.run(host=host, port=port, debug=debug)

    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n💥 Error crítico: {e}")
        raise
    finally:
        # 6. Limpieza explícita
        print("\n🧹 Realizando limpieza...")
        if 'server' in locals() and server.is_initialized():
            server.shutdown()
        if 'sdk_manager' in locals():
            sdk_manager.cleanup_all()
        print("✅ Aplicación terminada correctamente")


if __name__ == "__main__":
    main()