@echo off
echo ============================================
echo   Configuracion de Entorno - Comsulting
echo ============================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en PATH
    echo Por favor instala Python desde https://python.org
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Crear entorno virtual
echo Creando entorno virtual...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] No se pudo crear el entorno virtual
    pause
    exit /b 1
)

echo [OK] Entorno virtual creado
echo.

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

REM Actualizar pip
echo Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] No se pudieron instalar las dependencias
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Configuracion completada exitosamente!
echo ============================================
echo.
echo Para activar el entorno virtual en el futuro, ejecuta:
echo   venv\Scripts\activate
echo.
echo Para iniciar la aplicacion:
echo   python app.py
echo.
echo Para ejecutar analisis de productividad:
echo   python analisis_productividad.py
echo.
pause
