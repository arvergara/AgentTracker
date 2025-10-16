# Post-Deployment: Verificación en Render

**Fecha de Deploy**: 15 de octubre de 2025
**Commit**: feat: Sistema de permisos jerárquicos + 38 usuarios

---

## ✅ Cambios Desplegados

### Nuevas Funcionalidades
- ✅ Sistema de permisos jerárquicos (3 niveles)
- ✅ 38 usuarios del organigrama Oct 2025
- ✅ Jerarquía organizacional completa
- ✅ Carlos Valera agregado
- ✅ Áreas y servicios estándar

### Mejoras en Base de Datos
- ✅ Nuevos campos: `es_admin`, `reporte_a_id`
- ✅ Relaciones jerárquicas configuradas
- ✅ Sistema listo para importar 78K registros históricos

---

## 🔍 Pasos de Verificación Post-Deployment

### 1. Verificar que el Build fue Exitoso

1. Ve a: https://dashboard.render.com
2. Selecciona tu servicio **AgentTracker**
3. Ve a la pestaña **"Events"**
4. Verifica que el último deploy muestre: ✅ **"Live"**

**Esperado en Logs**:
```
🚀 Iniciando build de AgentTracker...
📦 Instalando dependencias...
🗄️  Inicializando base de datos y sistema...
✅ Database schema created
👥 No users found, initializing complete system...
✅ System initialized successfully
🎉 Build completed successfully!
```

### 2. Verificar la Aplicación

**URL de la App**: `https://[tu-servicio].onrender.com`

#### Test 1: Página de Login
1. Abre la URL de tu app
2. Deberías ver la página de login
3. ✅ **OK** si carga correctamente

#### Test 2: Login como Admin
**Credenciales**:
- Email: `bbulnes@comsulting.cl`
- Password: `comsulting2025`

**Verificar**:
- ✅ Login exitoso
- ✅ Redirige al dashboard
- ✅ Muestra mensaje de bienvenida

#### Test 3: Verificar Permisos Admin
Como Blanca Bulnes (admin):
- ✅ Puede ver menú "Personas"
- ✅ Ve listado de 38 personas
- ✅ Puede ver detalles de cualquier persona

#### Test 4: Login como Socia (Permisos Limitados)
**Credenciales**:
- Email: `mochagavia@comsulting.cl`
- Password: `comsulting2025`

**Verificar**:
- ✅ Login exitoso
- ✅ Ve solo su info + 5 subordinados (6 personas total)
- ✅ NO ve información de Ángeles Pérez (subordinada de Carolina Romero)

#### Test 5: Login como Usuario Regular
**Credenciales**:
- Email: `crodriguez@comsulting.cl`
- Password: `comsulting2025`

**Verificar**:
- ✅ Login exitoso
- ✅ Ve solo su propia información (1 persona)
- ✅ NO ve información de otros usuarios

### 3. Verificar Base de Datos

**Desde Render Shell**:
1. En el dashboard → Tu servicio → **"Shell"**
2. Ejecuta:

```bash
python << PYTHON
from app import app, db, Persona, Area, Servicio

with app.app_context():
    print(f"✅ Total personas: {Persona.query.count()}")
    print(f"✅ Administradores: {Persona.query.filter_by(es_admin=True).count()}")
    print(f"✅ Con supervisor: {Persona.query.filter(Persona.reporte_a_id != None).count()}")
    print(f"✅ Áreas: {Area.query.count()}")
    print(f"✅ Servicios: {Servicio.query.count()}")
PYTHON
```

**Resultado Esperado**:
```
✅ Total personas: 38
✅ Administradores: 3
✅ Con supervisor: 29
✅ Áreas: 5-6
✅ Servicios: 11+
```

---

## 🚨 Troubleshooting

### Problema 1: Build Falla

**Error**: "Database schema creation failed"

**Solución**:
1. Verifica los logs en Render
2. Asegúrate que `build.sh` tiene permisos de ejecución
3. Verifica que todos los modelos en `app.py` están correctos

### Problema 2: No se Crearon Usuarios

**Síntoma**: Login falla con "Usuario no encontrado"

**Solución desde Render Shell**:
```bash
python inicializar_sistema_completo.py
```

### Problema 3: Permisos No Funcionan

**Síntoma**: Admin no ve todos los usuarios

**Solución**:
```bash
python configurar_jerarquia_organigrama.py
```

### Problema 4: App No Carga

**Posibles causas**:
1. Error en `app.py`
2. Dependencias faltantes en `requirements.txt`
3. Variable de entorno `SECRET_KEY` no configurada

**Solución**:
1. Revisa logs en Render
2. Verifica Environment Variables
3. Re-deploy manual si es necesario

---

## ⚠️ IMPORTANTE: Base de Datos en Render

### SQLite No es Persistente

❌ **Los datos se borran en cada deploy** si usas SQLite en Render.

**Esto significa**:
- Cada deploy = usuarios se recrean desde cero
- Registros de horas NO persisten entre deploys
- NO es adecuado para producción real

### Solución: Migrar a PostgreSQL

Para datos persistentes, necesitas:

1. **Crear PostgreSQL Database en Render**
   - Dashboard → New + → PostgreSQL
   - Copiar la `DATABASE_URL`

2. **Agregar a Environment Variables**
   ```
   DATABASE_URL = postgresql://user:password@host/dbname
   ```

3. **Actualizar `requirements.txt`**
   ```
   psycopg2-binary==2.9.9
   ```

4. **Modificar `app.py`** (solo si usas SQLite hardcoded)
   ```python
   import os
   database_url = os.environ.get('DATABASE_URL')
   if database_url and database_url.startswith('postgres://'):
       database_url = database_url.replace('postgres://', 'postgresql://', 1)
   app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///comsulting_simplified.db'
   ```

5. **Re-deploy**
   - Los datos ahora serán persistentes
   - Se mantendrán entre deploys

### Importar Datos Históricos a PostgreSQL

**Después de migrar a PostgreSQL**:

1. Desde Render Shell:
```bash
# Solo necesario la primera vez después de migrar a PostgreSQL
python importar_historial_2024_2025.py
```

**Nota**: Este paso requiere el CSV `Historial2024-2025.csv` que NO está en Git por tamaño. Necesitarás subirlo manualmente o importarlo desde otra fuente.

---

## 📊 Métricas a Monitorear

### En Render Dashboard

1. **CPU Usage**: Debería estar < 50% en promedio
2. **Memory**: Debería estar < 80% del límite
3. **Response Time**: < 2 segundos
4. **Error Rate**: 0% idealmente

### Logs Importantes

Buscar estos mensajes en los logs:

✅ **Exitosos**:
```
✅ Database created successfully
✅ System initialized successfully
✅ 38 usuarios creados
✅ 3 administradores configurados
```

❌ **Errores a Investigar**:
```
❌ Error durante la importación
⚠️  Personas no encontradas
❌ Database is locked
```

---

## 🎯 Checklist Post-Deployment

- [ ] Build completado sin errores
- [ ] App responde en la URL de Render
- [ ] Login como admin funciona (`bbulnes@comsulting.cl`)
- [ ] Admin ve 38 personas
- [ ] Login como socia funciona (`mochagavia@comsulting.cl`)
- [ ] Socia ve solo 6 personas (ella + 5 subordinados)
- [ ] Login como usuario funciona (`crodriguez@comsulting.cl`)
- [ ] Usuario ve solo 1 persona (ella misma)
- [ ] Base de datos tiene 38 usuarios
- [ ] Base de datos tiene 3 admins
- [ ] Base de datos tiene 29 personas con supervisor
- [ ] Áreas y servicios creados

---

## 📞 Siguiente Paso

Si todo funciona correctamente, el siguiente paso es:

### Opción A: Continuar con SQLite (Solo Testing)
- ⚠️ Los datos se borran en cada deploy
- ✅ Bueno para pruebas rápidas
- ❌ NO usar para producción

### Opción B: Migrar a PostgreSQL (Recomendado)
- ✅ Datos persistentes
- ✅ Listo para producción
- ✅ Permite importar 78K registros históricos
- ✅ Mejor performance

### Opción C: Importar Datos Históricos (Después de PostgreSQL)
1. Subir `Historial2024-2025.csv` al servidor
2. Ejecutar `python importar_historial_2024_2025.py`
3. Esperar ~10 minutos
4. Verificar 78K registros importados

---

## ✅ Estado Esperado Final

Después de un deployment exitoso:

```
🎉 AgentTracker Deployed Successfully

👥 Users: 38
🔐 Admins: 3 (Blanca, Macarena, Jazmín)
👔 Supervisors: 6
📊 Hierarchy: 29 reporting relationships
🏢 Clients: 0 (se crean al registrar horas o importar histórico)
📂 Areas: 5-6
⚙️  Services: 11+
🔗 Live URL: https://[tu-servicio].onrender.com
```

---

**Documentación Completa**: Ver `SISTEMA_PERMISOS_JERARQUICOS.md`
**Usuarios**: Ver `USUARIOS_ORGANIGRAMA.md`
**Resumen Técnico**: Ver `RESUMEN_FINAL_IMPLEMENTACION.md`
