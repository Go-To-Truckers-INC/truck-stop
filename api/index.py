import sys
import os

# Agregar el directorio raíz al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar y crear la aplicación
from app.main import application

# Vercel necesita este objeto 'app'
app = application

# Vercel ejecutará esta aplicación
if __name__ == "__main__":
    app.run()