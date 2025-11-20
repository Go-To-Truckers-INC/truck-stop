import os
from dotenv import load_dotenv

# Cargar variables de entorno AL INICIO
load_dotenv()

from app.flask.flask_server import FlaskServer
from app.firebase.firebase_sdk import FirebaseSDK
from app.core.sdk_manager import SDKManager
from flask_bootstrap import Bootstrap4

# Importar blueprints
from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.companies import companies_bp
from app.routes.developers import developers_bp

def setup_sdks():
    """Configura y inicializa todos los SDKs de forma explícita"""
    sdk_manager = SDKManager()

    try:
        # Configuración explícita de Firebase SDK
        firebase_sdk = FirebaseSDK()

        if firebase_sdk.is_initialized():
            if sdk_manager.register_sdk('firebase', firebase_sdk):
                print("✅ Firebase SDK inicializado correctamente")
            else:
                print("⚠️  Firebase SDK no se pudo registrar en SDKManager")
        else:
            print("⚠️  Firebase SDK no inicializado - continuando sin Firebase")

    except Exception as e:
        print(f"⚠️  Error configurando Firebase SDK: {e}")
        print("ℹ️  Continuando sin Firebase...")

    return sdk_manager

import secrets
from flask import g



def create_app():
    """Factory function para crear la aplicación Flask - REQUERIDO por Elastic Beanstalk"""
    print("🚀 Creando aplicación Flask para Elastic Beanstalk...")

    try:
        # 1. Configurar SDKs
        print("📦 Configurando SDKs...")
        sdk_manager = setup_sdks()

        # 2. Crear servidor Flask
        server = FlaskServer('truck_stop_app')

        # 3. Configuración para producción
        config = {
            'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
            'DEBUG': False,  # Siempre False en producción
            'ENV': 'production',
            'TESTING': False,
            'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,
            'JSON_SORT_KEYS': False,
        }

        # 4. Inicializar servidor
        if not server.initialize():
            print("❌ Error inicializando el servidor Flask")
            return None

        # 5. Aplicar configuración
        server.set_config(config)

        # 6. INICIALIZAR BOOTSTRAP4
        bootstrap = Bootstrap4(server.app)
        print("✅ Bootstrap4 inicializado correctamente")

        # 7. Configurar CORS
        allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
        server.setup_cors(
            origins=allowed_origins,
            methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
            allow_headers=['Content-Type', 'Authorization', 'X-Requested-With']
        )

        # 8. Registrar todos los blueprints
        server.add_blueprint(main_bp)
        server.add_blueprint(auth_bp)
        server.add_blueprint(dashboard_bp)
        server.add_blueprint(companies_bp)
        server.add_blueprint(developers_bp)

        # 9. Health checks ESSENCIALES para EB
        @server.app.route('/')
        def root_health_check():
            return {'status': 'healthy', 'message': 'Truck Stop App'}, 200

        @server.app.route('/health')
        def health_check():
            return {'status': 'healthy'}, 200

        @server.app.route('/api/health')
        def api_health_check():
            return {
                'status': 'healthy',
                'service': 'truck-stop-app',
                'environment': os.getenv('FLASK_ENV', 'production')
            }, 200

        print("✅ Aplicación Flask configurada correctamente")
        return server.app

    except Exception as e:
        print(f"💥 Error creando la aplicación: {e}")
        import traceback
        traceback.print_exc()
        return None

# Para desarrollo local
if __name__ == "__main__":
    app = create_app()
    if app:
        print("🚀 Iniciando servidor en modo desarrollo...")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("❌ No se pudo iniciar la aplicación")