# Instrucciones para Ejecutar Importación en Render

## Problemas Identificados y Corregidos

### Problema 1: Transacciones abortadas (Commit 4ac362c)
El script fallaba porque:
1. **Error en transacción SQL**: Cuando ocurría un error, la transacción PostgreSQL quedaba abortada
2. **Falta de rollback**: El script no hacía `rollback()` después de errores
3. **Error**: `(psycopg2.errors.InFailedSqlTransaction) current transaction is aborted`

**Solución**:
✅ Agregado `conn.rollback()` en el bloque de error
✅ Captura detallada de errores (cliente, persona)
✅ Limitado output a primeros 10 errores
✅ Script de diagnóstico agregado (`diagnostico_render.py`)

### Problema 2: Secuencias PostgreSQL desincronizadas (Commit adb5705)
El script fallaba con:
1. **Error**: `duplicate key value violates unique constraint "servicios_pkey"`
2. **Causa**: Las secuencias de PostgreSQL no estaban sincronizadas con los IDs máximos
3. **Resultado**: Intentaba insertar con IDs que ya existían (19, 20, 21, etc.)

**Solución**:
✅ Agregada función `arreglar_secuencias()` que sincroniza todas las secuencias
✅ Ejecuta automáticamente al inicio del script de importación
✅ Script standalone `arreglar_secuencias.py` para uso independiente
✅ Sincroniza: personas, clientes, areas, servicios, tareas, registros_horas

## Pasos para Ejecutar en Render Shell

### 1. Acceder al Shell de Render

1. Ve a: https://dashboard.render.com
2. Selecciona tu servicio "AgentTracker"
3. Click en "Shell" en el menú lateral

### 2. Configurar Variables de Entorno

```bash
export DATABASE_URL="postgresql://agenttracker_db_user:SVoi2QQ0qt0Zye0QPzEj7g2lX9RJ2ANb@dpg-d3pb2i3ipnbc739ps5r0-a/agenttracker_db"
```

### 3. Instalar Dependencias

```bash
pip3 install pandas openpyxl sqlalchemy psycopg2-binary
```

### 4. (OPCIONAL) Ejecutar Diagnóstico Primero

Este paso es opcional pero recomendado para verificar el estado actual:

```bash
python3 diagnostico_render.py
```

Esto mostrará:
- ✅ Estructura de tablas
- ✅ Clientes existentes
- ✅ Personas existentes
- ✅ Registros actuales de horas (2025)
- ✅ Verificación de clientes del Excel

### 5. Arreglar Secuencias de PostgreSQL (CRÍTICO)

**NUEVO**: Antes de importar, ejecuta esto para evitar errores de "duplicate key":

```bash
python3 arreglar_secuencias.py
```

Esto sincroniza las secuencias auto-incrementales con los IDs existentes.

### 6. Ejecutar Importación Corregida

```bash
python3 importar_horas_produccion.py
```

**Nota**: El script ahora arregla las secuencias automáticamente, pero si aún ves errores de "duplicate key", ejecuta `arreglar_secuencias.py` primero.

### 7. Verificar Resultados

```bash
python3 verificar_datos_produccion.py
```

## Resultados Esperados

### Antes de la importación:
- Total registros 2025: ~30,000
- Total horas 2025: ~30,000

### Después de la importación:
- Total registros 2025: ~40,000+ (objetivo: 45,750)
- Total horas 2025: ~40,400+ (objetivo: 40,426.83)
- Diferencia: < 3% (aceptable)

## ¿Qué hace el script corregido?

1. **Crear 8 personas nuevas**:
   - María Marañón
   - Vicente Vera
   - Catalina Durán
   - Javiera Flores
   - Felipe Iglesias
   - Rosirene Clavero
   - Belén Castro
   - Nicolás Campos

2. **Mapear nombres correctamente**:
   - Excel → Base de datos (11 mapeos de personas)
   - Excel → Base de datos (3 mapeos de clientes)

3. **Importar ~9,000-10,000 registros nuevos**:
   - Filtrados para 2025 (Jan-Sep)
   - Evita duplicados
   - **NUEVO**: Hace rollback si hay error SQL
   - Continúa con el siguiente registro después de error

4. **Manejo de errores mejorado**:
   - Captura errores SQL individuales
   - Hace rollback de la transacción
   - Muestra detalles (cliente, persona)
   - Continúa con importación
   - Resume errores al final

## Clientes Mapeados

Los siguientes clientes del Excel se mapean a nombres existentes en producción:

- `CLÍNICAS` → `EBM`
- `FALABELLA` → `Falabella`
- `EMBAJADA ITALIA` → `Embajada de Italia`

## Áreas en Producción

Las siguientes áreas existen en producción:
- Asuntos Públicos
- Comunicaciones (área por defecto)
- Diseño
- Externas
- Internas
- Redes Sociales

## Solución de Problemas

### Error: "No module named 'pandas'"
```bash
pip3 install pandas openpyxl sqlalchemy psycopg2-binary
```

### Error: "No se encuentra el archivo Excel"
El archivo debe estar en el mismo directorio o en el directorio padre.
Verificar con: `ls -la | grep "Historial"`

### Error: "current transaction is aborted"
**Este error YA ESTÁ CORREGIDO** en el commit 4ac362c.
Si aún lo ves, verifica que Render haya desplegado la última versión:
```bash
git log -1 --oneline
# Debe mostrar: 4ac362c Fix: Agregar rollback en errores SQL...
```

### Render no tiene los últimos cambios
Espera 2-3 minutos para que Render auto-despliegue o:
1. Ve a dashboard de Render
2. Click en "Manual Deploy" → "Deploy latest commit"

## Contacto y Soporte

Si los números siguen sin cuadrar después de ejecutar estos scripts:
1. Ejecuta `diagnostico_render.py` y comparte el output
2. Ejecuta `verificar_datos_produccion.py` y comparte el output
3. Revisa los logs de errores mostrados durante la importación

---

**Última actualización**: Commit 4ac362c - Fix rollback en errores SQL
