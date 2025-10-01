# 🚀 Inicio Rápido en VS Code

## ⚡ Setup Automático (Recomendado)

### Windows
```bash
setup.bat
```

### Mac/Linux
```bash
chmod +x setup.sh
./setup.sh
```

Esto instalará todo automáticamente. Luego continúa en el paso "Abrir en VS Code".

---

## 📋 Setup Manual (Si el automático falla)

### 1. Crear Entorno Virtual

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

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Abrir en VS Code

```bash
code .
```

---

## 🎯 Primeros Pasos en VS Code

### 1. Instalar Extensiones Recomendadas

Al abrir el proyecto, VS Code te preguntará si quieres instalar las extensiones recomendadas. 

✅ **Clic en "Install All"**

O instálalas manualmente:
- Python (Microsoft)
- Pylance
- Python Debugger
- Better Jinja
- SQLite Viewer

### 2. Seleccionar Intérprete Python

1. `Ctrl+Shift+P` (o `Cmd+Shift+P` en Mac)
2. Escribe: "Python: Select Interpreter"
3. Selecciona el que está en `./venv/...`

### 3. Inicializar Base de Datos

**Opción A: Desde el navegador**
```bash
python app.py
```
Luego visita: http://localhost:5000/inicializar-datos

**Opción B: Desde Python**
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ DB Inicializada')"
```

---

## ▶️ Ejecutar la Aplicación

### Método 1: Debug (Recomendado)

1. Ve a la pestaña "Run and Debug" (`Ctrl+Shift+D`)
2. Selecciona "Flask: App Principal"
3. Presiona `F5` o el botón verde ▶️

**Ventajas:**
- ✅ Recarga automática al guardar cambios
- ✅ Puedes poner breakpoints
- ✅ Ver variables en tiempo real

### Método 2: Terminal

```bash
python app.py
```

### Método 3: Tareas de VS Code

1. `Ctrl+Shift+P`
2. "Tasks: Run Task"
3. Selecciona "Iniciar Flask App"

---

## 🔍 Debugging

### Poner Breakpoints

1. Haz clic en el margen izquierdo (antes del número de línea)
2. Aparecerá un círculo rojo 🔴
3. Ejecuta con `F5`
4. La ejecución se detendrá en ese punto

### Controles de Debug

| Acción | Tecla | Descripción |
|--------|-------|-------------|
| Continue | `F5` | Continuar hasta el siguiente breakpoint |
| Step Over | `F10` | Ejecutar línea actual |
| Step Into | `F11` | Entrar en la función |
| Step Out | `Shift+F11` | Salir de la función actual |
| Restart | `Ctrl+Shift+F5` | Reiniciar debugging |
| Stop | `Shift+F5` | Detener debugging |

### Ver Variables

Mientras debuggeas:
- Panel izquierdo: "Variables" muestra todas las variables locales
- Panel izquierdo: "Watch" te permite agregar expresiones a observar
- Hover: Pasa el mouse sobre cualquier variable para ver su valor

---

## 🛠️ Tareas Comunes

### Ejecutar Análisis de Productividad

**Opción 1: Debug**
1. Abre `analisis_productividad.py`
2. `F5` → Selecciona "Análisis de Productividad"

**Opción 2: Terminal**
```bash
python analisis_productividad.py
```

**Opción 3: Tarea**
- `Ctrl+Shift+P` → "Tasks: Run Task" → "Ejecutar Análisis de Productividad"

### Ver Base de Datos

1. Click derecho en `comsulting.db` (se crea al ejecutar app.py)
2. "Open Database"
3. Explora tablas y datos

### Formatear Código

**Auto (al guardar):**
Ya está configurado para formatear automáticamente con `Ctrl+S`

**Manual:**
- `Shift+Alt+F` (Windows/Linux)
- `Shift+Option+F` (Mac)

### Buscar en el Proyecto

- `Ctrl+P`: Buscar archivo por nombre
- `Ctrl+Shift+F`: Buscar texto en todos los archivos
- `Ctrl+F`: Buscar en archivo actual
- `F12` (sobre una función/variable): Ir a definición

---

## 📁 Estructura del Proyecto

```
comsulting-admin/
├── .vscode/              ← Configuración de VS Code
│   ├── settings.json     ← Configuración del editor
│   ├── launch.json       ← Configuración de debug
│   ├── tasks.json        ← Tareas personalizadas
│   └── extensions.json   ← Extensiones recomendadas
├── venv/                 ← Entorno virtual (ignorado por git)
├── templates/            ← Templates HTML (Jinja2)
├── static/
│   ├── css/
│   └── js/
├── app.py               ← 🔴 Aplicación principal Flask
├── analisis_productividad.py  ← 📊 Script de análisis
├── requirements.txt     ← Dependencias Python
├── .gitignore          ← Archivos a ignorar en git
├── comsulting.db       ← Base de datos SQLite (se crea al ejecutar)
└── *.md                ← Documentación
```

---

## ⌨️ Atajos Útiles

### Generales

| Acción | Atajo |
|--------|-------|
| Paleta de comandos | `Ctrl+Shift+P` |
| Terminal integrada | `Ctrl+`` |
| Buscar archivo | `Ctrl+P` |
| Buscar en archivos | `Ctrl+Shift+F` |
| Explorer (archivos) | `Ctrl+Shift+E` |
| Control de fuente (Git) | `Ctrl+Shift+G` |
| Extensiones | `Ctrl+Shift+X` |

### Edición

| Acción | Atajo |
|--------|-------|
| Comentar línea | `Ctrl+/` |
| Duplicar línea | `Shift+Alt+Down` |
| Mover línea | `Alt+Up/Down` |
| Múltiples cursores | `Alt+Click` |
| Seleccionar siguiente ocurrencia | `Ctrl+D` |
| Renombrar símbolo | `F2` |
| Formatear documento | `Shift+Alt+F` |

### Python Específico

| Acción | Atajo |
|--------|-------|
| Ejecutar archivo Python | `Ctrl+F5` |
| Ir a definición | `F12` |
| Ver definición (peek) | `Alt+F12` |
| Buscar referencias | `Shift+F12` |

---

## 🔧 Configuración Personalizada

Si quieres cambiar configuraciones:

1. `Ctrl+,` para abrir Settings
2. Busca lo que quieres cambiar
3. O edita directamente `.vscode/settings.json`

**Configuraciones útiles ya incluidas:**
- ✅ Auto-guardado: Desactivado (usa `Ctrl+S`)
- ✅ Auto-formateo al guardar: Activado
- ✅ Línea guía en columna 88 (PEP 8)
- ✅ Excluir archivos innecesarios del explorador
- ✅ IntelliSense mejorado para Python

---

## 🧪 Testing (Opcional)

### Crear Tests

Crea carpeta `tests/`:
```python
# tests/test_app.py
def test_index():
    from app import app
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200

def test_dashboard():
    from app import app
    with app.test_client() as client:
        response = client.get('/dashboard')
        assert response.status_code == 200
```

### Ejecutar Tests

**Terminal:**
```bash
pip install pytest
pytest -v
```

**VS Code:**
1. Instala extensión "Python Test Explorer"
2. Los tests aparecerán en la barra lateral
3. Click en ▶️ para ejecutar

---

## 📝 Git Integration

VS Code tiene Git integrado:

### Hacer Commit

1. `Ctrl+Shift+G` para abrir Source Control
2. Escribe tu mensaje de commit
3. `Ctrl+Enter` para hacer commit

### Ver Cambios

- Archivos modificados aparecen en la barra lateral (Source Control)
- Click en un archivo para ver diff
- Click en `+` para stage

### Comandos Git Útiles

```bash
# Inicializar repo
git init

# Estado
git status

# Agregar archivos
git add .

# Commit
git commit -m "mensaje"

# Ver historial
git log --oneline
```

---

## 🚨 Solución de Problemas

### No encuentra Python

1. Verifica instalación: `python --version`
2. Reinstala Python marcando "Add to PATH"
3. Reinicia VS Code

### Entorno virtual no activa

**Síntoma:** Terminal no muestra `(venv)`

**Solución Windows:**
```bash
venv\Scripts\activate
```

**Solución Mac/Linux:**
```bash
source venv/bin/activate
```

### Flask no arranca

**Síntoma:** Error "ModuleNotFoundError: No module named 'flask'"

**Solución:**
```bash
# Asegúrate de que venv está activado
pip install -r requirements.txt
```

### Puerto 5000 ocupado

**Síntoma:** "Address already in use"

**Solución:** Cambia el puerto en `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

### IntelliSense no funciona

1. `Ctrl+Shift+P`
2. "Python: Select Interpreter"
3. Selecciona `./venv/bin/python`
4. Reinicia VS Code

---

## 🎓 Recursos

### Documentación
- [VS Code Python](https://code.visualstudio.com/docs/python/python-tutorial)
- [Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)

### Videos (Recomendados)
- [VS Code Python Setup](https://www.youtube.com/watch?v=W--_EOzdTHk)
- [Flask Tutorial](https://www.youtube.com/watch?v=Z1RJmh_OqeA)

---

## ✅ Checklist de Verificación

Antes de empezar a desarrollar, verifica:

- [ ] Python instalado y en PATH
- [ ] VS Code instalado
- [ ] Entorno virtual creado (`venv/`)
- [ ] Dependencias instaladas (`pip list`)
- [ ] Extensiones Python instaladas
- [ ] Intérprete correcto seleccionado (./venv/...)
- [ ] `app.py` ejecuta sin errores
- [ ] Base de datos inicializada
- [ ] Aplicación accesible en http://localhost:5000
- [ ] Breakpoints funcionan en debug mode

---

## 🚀 ¡Listo para Desarrollar!

Ahora puedes:

1. **Explorar el código**: `Ctrl+P` → "app.py"
2. **Hacer cambios**: Edita archivos
3. **Ver resultados**: La app recarga automáticamente
4. **Debuggear**: Pon breakpoints con `F9`
5. **Ejecutar análisis**: `python analisis_productividad.py`

**Tip:** Mantén abierto el archivo `METODOLOGIA_PRODUCTIVIDAD.md` en una pestaña para referencia rápida mientras desarrollas.

---

*¿Dudas? Revisa `MIGRACION_VSC.md` para documentación completa*
*Problemas? Busca en la sección de Troubleshooting arriba*
