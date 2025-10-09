# Despliegue en Render

## Pasos para desplegar AgentTracker en Render

### 1. Crear Web Service en Render

1. Ve a https://dashboard.render.com/
2. Click en **"New +"** → **"Web Service"**
3. Conecta tu repositorio de GitHub: `https://github.com/arvergara/AgentTracker`
4. Configura el servicio:

### 2. Configuración del Web Service

**Configuración básica:**
- **Name:** `agenttracker` (o el nombre que prefieras)
- **Region:** Oregon (US West) o la más cercana
- **Branch:** `main`
- **Root Directory:** (dejar vacío)
- **Runtime:** `Python 3`
- **Build Command:** `./build.sh`
- **Start Command:** `gunicorn app:app`

**Configuración avanzada (Advanced):**

Agregar estas **Environment Variables**:

```
SECRET_KEY = [genera una key aleatoria segura, ej: openssl rand -hex 32]
PYTHON_VERSION = 3.11.0
```

**Plan:**
- Si tienes Render pagado, selecciona el plan que prefieras
- Mínimo recomendado: Starter ($7/mes) para mejor performance

### 3. Desplegar

1. Click en **"Create Web Service"**
2. Render automáticamente:
   - Clonará el repositorio
   - Ejecutará `build.sh` (instalará dependencias y creará la BD)
   - Iniciará la aplicación con Gunicorn
   - Te dará una URL: `https://agenttracker.onrender.com`

### 4. Configuración Inicial Post-Despliegue

Una vez desplegado, necesitas inicializar los datos:

**Opción A: Usando Render Shell**
1. En el dashboard de Render, ve a tu servicio
2. Click en **"Shell"** (en el menú lateral)
3. Ejecuta los scripts de importación:

```bash
python crear_usuarios.py
python importar_areas_servicios_tareas.py
python importar_clientes_ingresos.py
python actualizar_admin.py
```

**Opción B: Crear usuarios manualmente**
- Accede a la app
- Los scripts se pueden ejecutar desde tu máquina local apuntando a la base de datos de producción (no recomendado para SQLite)

### 5. Base de Datos Persistente (IMPORTANTE)

⚠️ **SQLite en Render NO es persistente** - Los datos se borran en cada deploy.

**Solución:** Migrar a PostgreSQL (recomendado para producción)

1. En Render dashboard: **New +** → **PostgreSQL**
2. Crea una base de datos PostgreSQL
3. Agrega a tu `requirements.txt`:
   ```
   psycopg2-binary==2.9.9
   ```
4. Modifica `app.py` para usar PostgreSQL:
   ```python
   import os

   # Usar PostgreSQL si está disponible, sino SQLite
   database_url = os.environ.get('DATABASE_URL')
   if database_url and database_url.startswith('postgres://'):
       database_url = database_url.replace('postgres://', 'postgresql://', 1)

   app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///comsulting_simplified.db'
   ```
5. En Environment Variables del Web Service:
   ```
   DATABASE_URL = [URL de tu PostgreSQL de Render]
   ```

### 6. Monitoreo

- **Logs:** En Render dashboard → Tu servicio → "Logs"
- **Métricas:** Ver uso de CPU, memoria, requests
- **Salud:** Render hace health checks automáticos

### 7. Dominios Personalizados (Opcional)

Si tienes un dominio:
1. En tu servicio → Settings → Custom Domain
2. Agrega tu dominio (ej: `agenttracker.comsulting.cl`)
3. Configura los DNS según instrucciones de Render

---

## Comandos Útiles

**Ver logs en tiempo real:**
- Desde Render dashboard → Logs

**Ejecutar comandos:**
- Render Shell (desde el dashboard)

**Reiniciar servicio:**
- Render dashboard → Manual Deploy → "Clear build cache & deploy"

---

## Troubleshooting

**Error: "Application failed to respond"**
- Revisa logs para ver errores de Python
- Verifica que gunicorn esté en requirements.txt
- Asegúrate que app.py exporte `app`

**Error: "Build failed"**
- Revisa que build.sh tenga permisos de ejecución
- Verifica que todas las dependencias estén en requirements.txt

**La base de datos se borra:**
- Normal con SQLite en Render
- Migra a PostgreSQL para persistencia

---

## Estructura de Archivos para Render

```
AgentTracker/
├── app.py                    # Aplicación Flask principal
├── requirements.txt          # Dependencias Python
├── build.sh                  # Script de build (ejecutable)
├── templates/                # Templates HTML
├── instance/                 # Base de datos SQLite (gitignored)
└── RENDER_DEPLOYMENT.md      # Esta guía
```

---

## Actualizar la Aplicación

1. Haz cambios en tu código local
2. Commit y push a GitHub:
   ```bash
   git add .
   git commit -m "feat: nueva funcionalidad"
   git push origin main
   ```
3. Render detecta el push y **redespliega automáticamente**

---

## Costos Estimados (Render)

- **Free Tier:** 750 horas/mes (app se "duerme" tras 15 min de inactividad)
- **Starter:** $7/mes (siempre activo, mejor performance)
- **PostgreSQL:** Free 90 días, luego $7/mes para 256MB

**Recomendado para producción:** Starter + PostgreSQL = $14/mes
