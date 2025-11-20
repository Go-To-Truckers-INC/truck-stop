import os
import sys

# Añadir el directorio actual al path de Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print(f"🚀 Iniciando aplicación desde: {current_dir}")

# Importar y crear la aplicación
try:
    from app.main import create_app

    application = create_app()

    if application:
        print("✅ Aplicación Flask creada exitosamente para Elastic Beanstalk")
    else:
        print("❌ Error: No se pudo crear la aplicación")
        sys.exit(1)

except Exception as e:
    print(f"💥 Error crítico al crear la aplicación: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Solo para desarrollo local
if __name__ == "__main__":
    print("🔧 Ejecutando en modo desarrollo...")
    application.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )