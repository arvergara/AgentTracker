#!/bin/bash

echo "============================================"
echo "  Configuración de Entorno - Comsulting"
echo "============================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ [ERROR] Python 3 no está instalado"
    echo "Por favor instala Python 3 desde https://python.org"
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"
echo ""

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ [ERROR] No se pudo crear el entorno virtual"
    exit 1
fi

echo "✅ Entorno virtual creado"
echo ""

# Activar entorno virtual
echo "🔄 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "⬆️  Actualizando pip..."
python -m pip install --upgrade pip

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ [ERROR] No se pudieron instalar las dependencias"
    exit 1
fi

echo ""
echo "============================================"
echo "  ✅ Configuración completada exitosamente!"
echo "============================================"
echo ""
echo "Para activar el entorno virtual en el futuro, ejecuta:"
echo "  source venv/bin/activate"
echo ""
echo "Para iniciar la aplicación:"
echo "  python app.py"
echo ""
echo "Para ejecutar análisis de productividad:"
echo "  python analisis_productividad.py"
echo ""
echo "Para abrir en VS Code:"
echo "  code ."
echo ""
