#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Iniciando build de AgentTracker..."

# Install dependencies
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Initialize database schema ONLY (no data)
echo "🗄️  Creando schema de base de datos..."
python << PYTHON
from app import app, db

with app.app_context():
    # Solo crear las tablas
    db.create_all()
    print("✅ Database schema created")

print("🎉 Build completed successfully!")
print("ℹ️  Use Shell to initialize data with: python inicializar_sistema_completo.py")
PYTHON
