# 🚨 PASOS URGENTES - Restaurar AgentTracker en Render

## ❌ PROBLEMA ACTUAL
Cada deploy de Render borra TODOS los datos porque SQLite no es persistente:
- 78,853 registros de horas → **BORRADOS**
- 32 clientes → **BORRADOS**
- 67 servicios → **BORRADOS**
- 6 áreas → **BORRADAS**
- Ingresos mensuales → **BORRADOS**

## ✅ SOLUCIÓN (15 minutos)

### PASO 1: Crear PostgreSQL en Render (3 min)

1. Ve a: https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Configuración:
   ```
   Name: agenttracker-db
   Database: agenttracker
   Region: Oregon (US West)
   Plan: Free
   ```
4. Click **"Create Database"**
5. **ESPERA** que aparezca "Available" (1-2 min)

### PASO 2: Copiar URL de Conexión (1 min)

1. En la página de la DB recién creada
2. Busca la sección **"Connections"**
3. Copia **"Internal Database URL"**
   - Empieza con: `postgres://`
   - Ejemplo: `postgres://user:pass123@dpg-xxxxx.oregon-postgres.render.com/agenttracker`
4. **GUÁRDALA** en un lugar seguro

### PASO 3: Configurar Web Service (2 min)

1. Ve a tu Web Service: https://dashboard.render.com/web/srv-xxxxx
2. Click **"Environment"** (menú izquierdo)
3. Scroll abajo, click **"Add Environment Variable"**
4. Agregar:
   ```
   Key:   DATABASE_URL
   Value: [PEGA AQUÍ LA URL DEL PASO 2]
   ```
5. Click **"Save Changes"**
6. Render empezará a re-deployar automáticamente

### PASO 4: Esperar Deploy (3-5 min)

1. Ve a **"Logs"** tab
2. Espera a ver:
   ```
   ==> Build successful
   ==> Starting service...
   👥 No users found, initializing complete system...
   ✓ 38 usuarios creados
   ```
3. Cuando veas "Your service is live", continúa

### PASO 5: Restaurar Datos Históricos (5 min)

1. En tu Web Service, click tab **"Shell"**
2. Ejecuta los siguientes comandos uno por uno:

```bash
# 1. Verificar que PostgreSQL funciona
python3 -c "from app import db, Persona; print(f'Personas: {Persona.query.count()}')"
# Debe mostrar: Personas: 38

# 2. Importar TODOS los datos históricos
python3 importar_desde_json.py
```

3. Deberías ver:
```
✓ 32 clientes importados
✓ 6 áreas importadas
✓ 67 servicios importados
✓ 791 tareas importadas
✓ 78,853 registros de horas importados
```

### PASO 6: Verificar que Funciona (1 min)

1. Ve a: https://agenttracker.onrender.com
2. Login con: `bbulnes@comsulting.cl` / `blanca2025`
3. Deberías ver:
   - Dashboard con métricas reales
   - "Mis Horas" con todos los registros históricos
   - Clientes con datos
   - Personal activo

## 🎉 LISTO

Ahora PostgreSQL es **PERMANENTE**:
- ✅ Los datos NO se borran en deploys futuros
- ✅ Las 78,853 horas están seguras
- ✅ Todos los clientes y servicios restaurados
- ✅ Sistema operativo para noviembre

## ⚠️ MUY IMPORTANTE

**NO VUELVAS A HACER DEPLOY** hasta completar estos pasos, o perderás los datos otra vez.

Una vez configurado PostgreSQL, puedes deployar cuando quieras - los datos persisten.

## 🆘 Si algo falla

**Error común 1**: "could not connect to server"
- Solución: Verifica que copiaste bien la DATABASE_URL completa

**Error común 2**: Shell no responde
- Solución: Espera 30 segundos y refresca la página

**Error común 3**: importar_desde_json.py no existe
- Solución: Verifica que el último deploy terminó correctamente en "Logs"

**Error común 4**: Archivo JSON muy grande
- Solución: El import puede tomar 5-10 minutos, sé paciente

## 📞 Necesitas ayuda?

Avísame en qué paso estás y qué mensaje de error ves.
