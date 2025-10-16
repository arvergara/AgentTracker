# Configurar PostgreSQL en Render - URGENTE

## ⚠️ PROBLEMA ACTUAL
SQLite se resetea en cada deploy de Render, perdiendo TODOS los datos (78,853 registros históricos).

## ✅ SOLUCIÓN: PostgreSQL Persistente

### Paso 1: Crear Base de Datos PostgreSQL en Render

1. Ve a https://dashboard.render.com
2. Click en **"New +"** → **"PostgreSQL"**
3. Configura:
   - **Name**: `agenttracker-db`
   - **Database**: `agenttracker`
   - **User**: (autogenerado)
   - **Region**: Oregon (US West)
   - **Plan**: **Free** (suficiente para empezar)
4. Click **"Create Database"**
5. Espera 1-2 minutos a que se cree

### Paso 2: Copiar la URL de Conexión

1. En la página de la base de datos recién creada
2. Busca **"Internal Database URL"**
3. Copia la URL completa (empieza con `postgres://`)
4. **GUARDA ESTA URL** - la necesitarás en el siguiente paso

Ejemplo de URL:
```
postgres://user:password@dpg-xxxxx-a.oregon-postgres.render.com/agenttracker_db
```

### Paso 3: Configurar Variable de Entorno en el Web Service

1. Ve a tu Web Service: https://dashboard.render.com/web/srv-xxx (AgentTracker)
2. Click en **"Environment"** en el menú izquierdo
3. Click **"Add Environment Variable"**
4. Agrega:
   - **Key**: `DATABASE_URL`
   - **Value**: [PEGA LA URL DE POSTGRESQL DEL PASO 2]
5. Click **"Save Changes"**

### Paso 4: Deploy Automático

Render detectará los cambios y hará un nuevo deploy automáticamente con:
- ✅ PostgreSQL configurado
- ✅ Tablas creadas automáticamente
- ✅ Sistema inicializado con 38 usuarios

### Paso 5: Importar Datos Históricos

Después del deploy, ejecuta estos comandos en la Shell de Render:

1. Ve a tu Web Service → **"Shell"** tab
2. Ejecuta:
```bash
# Verificar que las tablas existen
python3 -c "from app import db, Persona; print(f'Personas: {Persona.query.count()}')"

# Importar datos desde JSON (si tienes el archivo exportar_datos_2024_2025.json)
python3 importar_desde_json.py
```

Si no tienes el JSON, necesitas volver a importar desde el CSV:
```bash
python3 importar_historial_2024_2025.py
```

## 📊 Ventajas de PostgreSQL

- ✅ **Persistencia**: Los datos NO se pierden en deploys
- ✅ **Rendimiento**: Mejor para 78K+ registros
- ✅ **Confiabilidad**: Base de datos profesional
- ✅ **Gratis**: Plan free de Render suficiente para empezar
- ✅ **Backups**: Render hace backups automáticos

## 🚨 IMPORTANTE

1. **NO hagas más deploys hasta configurar PostgreSQL** - perderás los datos otra vez
2. Después de configurar PostgreSQL, los datos se mantienen permanentemente
3. El archivo `exportar_datos_json.py` ya generó un respaldo de 15.33 MB con todos los datos

## ⏱️ Tiempo Estimado

- Crear PostgreSQL: 2 minutos
- Configurar variable: 1 minuto
- Deploy automático: 3-5 minutos
- Importar datos: 5-10 minutos
- **TOTAL: ~15 minutos**

## 🆘 Si tienes problemas

Revisa los logs en Render:
```
Web Service → Logs
```

Errores comunes:
- "could not connect to server": La DATABASE_URL está mal copiada
- "relation does not exist": Las tablas no se crearon - revisar build.sh
