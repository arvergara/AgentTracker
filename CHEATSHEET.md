# ⚡ Cheatsheet - Comandos Esenciales

## 🚀 Setup Inicial (Una Sola Vez)

```bash
# Windows
setup.bat

# Mac/Linux
chmod +x setup.sh
./setup.sh
```

---

## 🔄 Activar Entorno (Cada Sesión)

```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

---

## ▶️ Ejecutar Aplicación

```bash
# Terminal
python app.py

# O en VS Code
F5 → "Flask: App Principal"
```

**Abrir en navegador:** http://localhost:5000

---

## 📊 Análisis de Productividad

```bash
# Terminal
python analisis_productividad.py

# O en VS Code
F5 → "Análisis de Productividad"
```

---

## 🎯 Primeros Pasos

### 1. Cargar Datos de Prueba
```
http://localhost:5000/inicializar-datos
```

### 2. Ver Dashboard
```
http://localhost:5000/dashboard
```

### 3. Explorar Código
```
Ctrl+P → "app.py"
```

---

## ⌨️ Atajos VS Code Esenciales

| Acción | Windows/Linux | Mac |
|--------|--------------|-----|
| Paleta comandos | `Ctrl+Shift+P` | `Cmd+Shift+P` |
| Terminal | `Ctrl+`` | `Ctrl+`` |
| Buscar archivo | `Ctrl+P` | `Cmd+P` |
| Debug (Start) | `F5` | `F5` |
| Breakpoint | `F9` | `F9` |
| Formatear | `Shift+Alt+F` | `Shift+Option+F` |
| Comentar | `Ctrl+/` | `Cmd+/` |

---

## 🐛 Debugging

```python
# Método 1: Breakpoints en VS Code
# Click en margen izquierdo → 🔴 → F5

# Método 2: Print debugging
print(f"Debug: {variable}")

# Método 3: PDB (Python Debugger)
import pdb; pdb.set_trace()
```

**Controles:**
- `F5` = Continue
- `F10` = Step Over
- `F11` = Step Into
- `Shift+F11` = Step Out

---

## 📝 Git Básico

```bash
# Inicializar
git init

# Ver cambios
git status

# Agregar archivos
git add .

# Commit
git commit -m "Descripción del cambio"

# Ver historial
git log --oneline

# Crear rama
git checkout -b feature/nueva-funcionalidad
```

---

## 📦 Gestión de Paquetes

```bash
# Instalar nuevo paquete
pip install nombre-paquete

# Guardar dependencias
pip freeze > requirements.txt

# Instalar desde requirements
pip install -r requirements.txt

# Listar instalados
pip list
```

---

## 🗄️ Base de Datos

```bash
# Ver base de datos en VS Code
# Click derecho en comsulting.db → "Open Database"

# Reiniciar base de datos
rm comsulting.db
python app.py
# Luego: http://localhost:5000/inicializar-datos
```

---

## 🔍 Búsqueda en Proyecto

```bash
# Buscar archivo por nombre
Ctrl+P → escribe nombre

# Buscar texto en todos los archivos
Ctrl+Shift+F → escribe texto

# Buscar en archivo actual
Ctrl+F → escribe texto

# Ir a definición
F12 (sobre función/variable)

# Buscar referencias
Shift+F12
```

---

## 🧪 Testing (Opcional)

```bash
# Instalar pytest
pip install pytest

# Ejecutar tests
pytest -v

# Con coverage
pip install pytest-cov
pytest --cov=app tests/
```

---

## 🛠️ Tareas Comunes

### Formatear Todo el Código
```bash
pip install black
black *.py
```

### Verificar Errores
```bash
pip install flake8
flake8 *.py --max-line-length=88
```

### Generar Documentación
```bash
pip install sphinx
sphinx-quickstart docs
```

---

## 🚨 Troubleshooting Rápido

### Error: "python no reconocido"
```bash
# Reinstala Python marcando "Add to PATH"
# Reinicia VS Code
```

### Error: "No module named flask"
```bash
# Activa venv primero
pip install -r requirements.txt
```

### Puerto 5000 ocupado
```python
# En app.py, cambia:
app.run(debug=True, host='0.0.0.0', port=8080)
```

### IntelliSense no funciona
```bash
# Ctrl+Shift+P
# "Python: Select Interpreter"
# Selecciona ./venv/bin/python
```

---

## 📁 Archivos Importantes

| Archivo | Descripción |
|---------|-------------|
| `app.py` | Aplicación Flask principal |
| `analisis_productividad.py` | Script de reportes |
| `requirements.txt` | Dependencias Python |
| `templates/` | HTML Templates (Jinja2) |
| `static/` | CSS, JS, imágenes |
| `comsulting.db` | Base de datos SQLite |
| `.vscode/` | Configuración VS Code |

---

## 📚 Documentación Clave

| Documento | Para Qué |
|-----------|----------|
| `README_VSCODE.md` | Guía completa VS Code |
| `MIGRACION_VSC.md` | Migración detallada |
| `METODOLOGIA_PRODUCTIVIDAD.md` | Entender fórmulas |
| `GUIA_PRACTICA.md` | Casos de uso |
| `INICIO_RAPIDO.md` | Instalación |

---

## 🎯 Workflow Típico

```bash
1. Abrir VS Code
   code .

2. Activar entorno
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate     # Windows

3. Ejecutar app
   F5 → "Flask: App Principal"

4. Hacer cambios
   Editar archivos

5. Ver resultados
   http://localhost:5000
   (recarga automáticamente)

6. Commit
   Ctrl+Shift+G → Message → Ctrl+Enter
```

---

## 🌟 Tips Pro

1. **Múltiples terminales**: `Ctrl+Shift+`` para nueva terminal
2. **Split editor**: `Ctrl+\` para dividir pantalla
3. **Zen mode**: `Ctrl+K Z` para modo sin distracciones
4. **Command palette**: `Ctrl+Shift+P` es tu mejor amigo
5. **Quick fix**: `Ctrl+.` para sugerencias de corrección
6. **Navegar back**: `Alt+Left` después de F12

---

## 📱 Endpoints Principales

| URL | Descripción |
|-----|-------------|
| `/` | Inicio |
| `/dashboard` | Dashboard principal |
| `/personas` | Gestión de personas |
| `/clientes` | Gestión de clientes |
| `/horas` | Registro de horas |
| `/inicializar-datos` | Cargar datos de prueba |
| `/api/capacidad/<meses>` | API capacidad |
| `/api/productividad/<id>/<meses>` | API productividad |

---

## 🎨 Extensiones Esenciales

✅ **Ya instaladas** (si seguiste setup):
- Python (Microsoft)
- Pylance
- Python Debugger
- Better Jinja
- SQLite Viewer

💡 **Recomendadas adicionales**:
- GitLens - Git superpowers
- Error Lens - Ver errores inline
- Material Icon Theme - Iconos bonitos
- Auto Rename Tag - HTML tags
- IntelliCode - AI completions

---

## 💾 Backup Rápido

```bash
# Backup base de datos
cp comsulting.db backups/comsulting_$(date +%Y%m%d).db

# Backup código
git commit -am "Backup: descripción"
git push  # si tienes repo remoto
```

---

## 🆘 Ayuda Rápida

**¿Cómo hago X?**
1. `Ctrl+Shift+P` → buscar comando
2. Buscar en documentación: `README_VSCODE.md`
3. Google: "vscode python [tu pregunta]"

**¿Error al ejecutar?**
1. Ver terminal: `Ctrl+``
2. Ver problemas: `Ctrl+Shift+M`
3. Verificar entorno: `which python` (Mac) o `where python` (Windows)

---

**💡 Tip Final:** Imprime esta página y mantenla cerca mientras aprendes!

---

*Cheatsheet v1.0 - Sistema Comsulting*
*Para documentación completa: README_VSCODE.md*
