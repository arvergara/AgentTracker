#!/bin/bash

# Script de inicio rápido para Comsulting Admin System

echo "🚀 Iniciando Comsulting Admin System..."
echo ""

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    echo "Por favor, instala Python 3.8 o superior"
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"
echo ""

# Instalar dependencias si es necesario
if [ ! -d "venv" ]; then
    echo "📦 Instalando dependencias..."
    pip3 install -r requirements.txt --break-system-packages
    echo ""
fi

# Verificar si la base de datos existe
if [ ! -f "comsulting.db" ]; then
    echo "⚠️  Base de datos no encontrada"
    echo "La base de datos se creará automáticamente al iniciar la aplicación"
    echo "Recuerda visitar http://localhost:5000/inicializar-datos para cargar datos de prueba"
    echo ""
fi

# Iniciar la aplicación
echo "🌐 Iniciando servidor en http://localhost:5000"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 app.py
