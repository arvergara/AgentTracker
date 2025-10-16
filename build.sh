#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Iniciando build de AgentTracker..."

# Install dependencies
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Initialize database and system
echo "🗄️  Inicializando base de datos y sistema..."
python << PYTHON
from app import app, db, Persona

with app.app_context():
    # Crear esquema
    db.create_all()
    print("✅ Database schema created")

    # Verificar si ya hay usuarios
    if Persona.query.count() == 0:
        print("👥 No users found, initializing complete system...")

        # Ejecutar inicialización completa
        import subprocess
        import sys

        try:
            # Inicializar sistema completo (usuarios + jerarquía + áreas)
            result = subprocess.run([sys.executable, 'inicializar_sistema_completo.py'],
                                  capture_output=True, text=True, check=True)
            print(result.stdout)
            print("✅ System initialized successfully")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Error during initialization: {e.stderr}")
            print("Continuing with basic setup...")

            # Fallback: solo crear áreas básicas
            subprocess.run([sys.executable, 'crear_areas_iniciales.py'], check=False)
    else:
        print(f"✅ Database already has {Persona.query.count()} users - skipping initialization")

print("🎉 Build completed successfully!")
PYTHON
