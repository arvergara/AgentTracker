# 🚀 Guía de Migración a Visual Studio Code

## Método 1: Descarga Directa (Más Simple)

### Paso 1: Descargar los Archivos

Los archivos están en `/mnt/user-data/outputs/`. Puedes:

**Opción A: Descargar carpeta completa desde el navegador**
1. En Claude.ai, haz clic en los archivos que aparecen en el chat
2. Descarga cada archivo uno por uno
3. Organízalos en una carpeta local

**Opción B: Crear un ZIP (más rápido)**
```bash
# En la terminal de Claude, ejecuta:
cd /mnt/user-data/outputs
tar -czf comsulting_app.tar.gz *.py *.md *.txt *.sh templates/ static/

# Esto creará comsulting_app.tar.gz que puedes descargar
```

### Paso 2: Crear Carpeta del Proyecto

En tu computadora:
```bash
# Windows
mkdir C:\Proyectos\comsulting-admin
cd C:\Proyectos\comsulting-admin

# Mac/Linux
mkdir -p ~/Proyectos/comsulting-admin
cd ~/Proyectos/comsulting-admin
```

### Paso 3: Extraer Archivos

Copia todos los archivos descargados a esta carpeta manteniendo la estructura:

```
comsulting-admin/
├── app.py
├── analisis_productividad.py
├── requirements.txt
├── start.sh
├── *.md (todos los documentos)
├── templates/
│   └── *.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

### Paso 4: Abrir en VS Code

```bash
code .
```

O desde VS Code: `File > Open Folder` → Selecciona la carpeta

---

## Paso 5: Configurar el Entorno en VS Code

### A. Instalar Extensiones Recomendadas

Abre la paleta de comandos (`Ctrl+Shift+P` o `Cmd+Shift+P`) y busca:

1. **Python** (Microsoft) - Esencial
2. **Pylance** (Microsoft) - IntelliSense mejorado
3. **Python Debugger** - Para debugging
4. **autoDocstring** - Documentación automática
5. **Better Jinja** - Sintaxis de templates HTML
6. **SQLite Viewer** - Ver base de datos

Opcionales pero útiles:
- **GitLens** - Si usarás Git
- **Material Icon Theme** - Iconos bonitos
- **Error Lens** - Ver errores inline

### B. Crear Entorno Virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Verás `(venv)` al inicio de tu terminal.

### C. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### D. Configurar VS Code para el Proyecto

Crea una carpeta `.vscode` en la raíz con estos archivos:

**`.vscode/settings.json`**
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/.pytest_cache": true
    },
    "python.analysis.typeCheckingMode": "basic"
}
```

**`.vscode/launch.json`** (Para debugging)
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Flask App",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "app.py",
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "1"
            },
            "args": [
                "run",
                "--host=0.0.0.0",
                "--port=5000"
            ],
            "jinja": true,
            "justMyCode": true
        },
        {
            "name": "Análisis Productividad",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/analisis_productividad.py",
            "console": "integratedTerminal"
        }
    ]
}
```

**`.vscode/extensions.json`** (Recomienda extensiones al equipo)
```json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.debugpy",
        "wholroyd.jinja",
        "alexcvzz.vscode-sqlite"
    ]
}
```

---

## Paso 6: Probar que Todo Funciona

### A. Inicializar Base de Datos

```bash
# Activa el entorno virtual primero
python app.py
```

Verás algo como:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
```

### B. Cargar Datos de Prueba

Abre en el navegador:
```
http://localhost:5000/inicializar-datos
```

### C. Explorar la Aplicación

```
http://localhost:5000
```

### D. Ejecutar Script de Análisis

En otra terminal (con venv activado):
```bash
python analisis_productividad.py
```

---

## Paso 7: Configurar Git (Opcional pero Recomendado)

### A. Inicializar Repositorio

```bash
git init
```

### B. Crear `.gitignore`

```bash
# Crear archivo .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Flask
instance/
.webassets-cache
*.db

# VS Code
.vscode/
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json

# OS
.DS_Store
Thumbs.db

# Project specific
comsulting.db
*.log
EOF
```

### C. Primer Commit

```bash
git add .
git commit -m "Initial commit: Sistema Comsulting v2.0"
```

### D. Conectar con GitHub (Opcional)

```bash
# Crea un repo en GitHub primero, luego:
git remote add origin https://github.com/tu-usuario/comsulting-admin.git
git branch -M main
git push -u origin main
```

---

## Estructura Final Recomendada

```
comsulting-admin/
├── .vscode/              # Configuración VS Code
│   ├── settings.json
│   ├── launch.json
│   └── extensions.json
├── venv/                 # Entorno virtual (ignorado por git)
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   └── ...
├── .gitignore           # Archivos a ignorar
├── app.py               # App principal
├── analisis_productividad.py
├── requirements.txt
├── README.md
├── METODOLOGIA_PRODUCTIVIDAD.md
└── ... (otros .md)
```

---

## Desarrollo en VS Code: Tips Útiles

### Atajos de Teclado Esenciales

| Acción | Windows/Linux | Mac |
|--------|--------------|-----|
| Paleta de comandos | `Ctrl+Shift+P` | `Cmd+Shift+P` |
| Terminal integrada | `Ctrl+`` | `Ctrl+`` |
| Buscar archivo | `Ctrl+P` | `Cmd+P` |
| Buscar en archivos | `Ctrl+Shift+F` | `Cmd+Shift+F` |
| Ir a definición | `F12` | `F12` |
| Renombrar símbolo | `F2` | `F2` |
| Formatear código | `Shift+Alt+F` | `Shift+Option+F` |

### Ejecutar desde VS Code

**Opción 1: Debug (Recomendado)**
1. Pon breakpoints haciendo clic a la izquierda del número de línea
2. Presiona `F5` o ve a `Run > Start Debugging`
3. Selecciona "Flask App"

**Opción 2: Terminal Integrada**
```bash
# Terminal > New Terminal
python app.py
```

### Ver Base de Datos

1. Instala extensión "SQLite Viewer"
2. Click derecho en `comsulting.db`
3. "Open Database"

### Trabajar con Templates

Los archivos `.html` en `templates/` tienen Jinja2 syntax.
Con la extensión "Better Jinja" tendrás:
- Syntax highlighting
- Autocompletado
- Snippets

---

## Workflows Comunes

### 1. Agregar Nueva Funcionalidad

```bash
# Crear nueva rama (si usas Git)
git checkout -b feature/nueva-funcionalidad

# Editar código en VS Code
# Probar con F5 (debug)

# Commit
git add .
git commit -m "feat: descripción de la funcionalidad"

# Merge a main
git checkout main
git merge feature/nueva-funcionalidad
```

### 2. Debugging

```python
# En app.py, agrega breakpoints o:
import pdb; pdb.set_trace()  # Para debugger manual

# O usa los breakpoints de VS Code (más fácil)
# Click en el margen izquierdo → círculo rojo
# F5 para ejecutar en modo debug
# F10 para siguiente línea
# F11 para entrar en función
```

### 3. Testing

Crea `tests/test_app.py`:
```python
import pytest
from app import app, db

def test_index():
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200
```

Ejecutar:
```bash
pip install pytest
pytest
```

### 4. Exportar Requerimientos Actualizados

Si instalas nuevas librerías:
```bash
pip freeze > requirements.txt
```

---

## Solución de Problemas

### Error: "python no reconocido"

**Windows:**
1. Instala Python desde python.org
2. Marca "Add Python to PATH" durante instalación
3. Reinicia VS Code

**Mac:**
```bash
brew install python3
```

### Error: "venv no funciona"

```bash
# Windows
python -m pip install --upgrade pip
python -m venv venv

# Mac/Linux
python3 -m pip install --upgrade pip
python3 -m venv venv
```

### Error: "Cannot find module flask"

```bash
# Asegúrate de que venv está activado (debe ver (venv) en terminal)
pip install -r requirements.txt
```

### Puerto 5000 ocupado

Cambia en `app.py` la última línea:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Cambiar puerto
```

O en `.vscode/launch.json`:
```json
"args": ["run", "--host=0.0.0.0", "--port=8080"]
```

---

## Recomendaciones Adicionales

### 1. Instalar Herramientas de Desarrollo

```bash
pip install black flake8 pylint
```

- **black**: Formateador automático
- **flake8**: Linter (encuentra errores)
- **pylint**: Análisis de código

### 2. Pre-commit Hooks (Opcional)

```bash
pip install pre-commit

# Crear .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
EOF

pre-commit install
```

### 3. Documentación con Sphinx (Opcional)

Para generar docs automáticas:
```bash
pip install sphinx sphinx-rtd-theme
sphinx-quickstart docs
```

---

## Checklist Final

- [ ] Carpeta creada y archivos copiados
- [ ] VS Code abierto en la carpeta
- [ ] Extensiones Python instaladas
- [ ] Entorno virtual creado y activado
- [ ] `requirements.txt` instalado
- [ ] Archivos de configuración `.vscode/` creados
- [ ] `app.py` ejecuta sin errores
- [ ] Base de datos inicializada
- [ ] Aplicación accesible en http://localhost:5000
- [ ] Git inicializado (opcional)
- [ ] `.gitignore` configurado

---

## Próximos Pasos

1. **Familiarízate con el código**: Lee `app.py` línea por línea
2. **Prueba las funcionalidades**: Usa el dashboard
3. **Ejecuta análisis**: `python analisis_productividad.py`
4. **Lee la documentación**: Especialmente `METODOLOGIA_PRODUCTIVIDAD.md`
5. **Empieza a desarrollar**: ¡Agrega tus propias mejoras!

---

## Recursos Útiles

- **VS Code Python**: https://code.visualstudio.com/docs/python/python-tutorial
- **Flask**: https://flask.palletsprojects.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Git**: https://git-scm.com/book/es/v2

---

¡Listo! Ahora tienes todo el proyecto configurado en VS Code y puedes continuar el desarrollo profesionalmente. 🚀
