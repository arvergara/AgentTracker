# Instrucciones para Importar Horas a Producción (Render)

## Problema Resuelto

AgentTracker tenía **10,325 horas faltantes (-25.5%)** en comparación con el archivo Excel TD 2025.

**Causa**: Nombres de personas en Excel (Harvest) no coincidían exactamente con nombres en la base de datos.

## Solución

Se creó el script `importar_horas_produccion.py` que:
- Mapea correctamente los nombres de personas
- Crea 8 personas faltantes en la BD
- Importa ~9,500 registros faltantes
- Reduce la diferencia de -25.5% a solo **-2.8%**

## Cómo Ejecutar el Script en Render

### Opción 1: Shell de Render (Recomendado)

1. **Acceder al Dashboard de Render**
   - Ve a https://dashboard.render.com
   - Selecciona el servicio `AgentTracker`

2. **Abrir Shell**
   - En el menú lateral, click en "Shell"
   - Esto abre una terminal en el servidor de producción

3. **Instalar dependencias adicionales** (si es necesario)
   ```bash
   pip install openpyxl pandas sqlalchemy psycopg2-binary
   ```

4. **Ejecutar el script**
   ```bash
   python importar_horas_produccion.py
   ```

5. **Monitorear la salida**
   - El script mostrará el progreso
   - Cada 5,000 registros muestra update
   - Al final muestra un resumen completo

### Opción 2: Desde tu computadora local

Si tienes la URL externa de PostgreSQL de Render:

1. **Configurar DATABASE_URL**
   ```bash
   export DATABASE_URL="postgresql://user:password@dpg-xxxxx.oregon-postgres.render.com/agenttracker_db"
   ```

2. **Instalar dependencias localmente**
   ```bash
   pip install openpyxl pandas sqlalchemy psycopg2-binary
   ```

3. **Ejecutar el script**
   ```bash
   cd /ruta/a/AgentTracker
   python importar_horas_produccion.py
   ```

## Qué Hace el Script

### 1. Crea Personas Faltantes
- María Marañón
- Vicente Vera
- Catalina Durán
- Javiera Flores
- Felipe Iglesias
- Rosirene Clavero
- Belén Castro
- Nicolás Campos

### 2. Mapea Nombres Correctamente

| Excel (Harvest) | Base de Datos |
|-----------------|---------------|
| Ángeles Pérez | María De Los Ángeles Pérez |
| Andrés Azócar | Raúl Andrés Azócar |
| Nidia Millahueique | Juana Nidia Millahueique |
| Bernardita Ochagavía | María Bernardita Ochagavia |
| Ignacio Echevería | Luis Ignacio Echeverría |
| Ignacio Díaz | Ignacio Diaz |
| Liliana Cortés | Liliana Cortes |
| Sofía Martinez | Sofía Martínez |
| Víctor Guillou | Victor Guillou |
| Hernan Díaz Diseño | Hernán Díaz |

### 3. Importa Registros de 2025 (ene-sep)
- Lee el archivo `Historial 2024-2025.xlsx`
- Filtra registros de 2025 (enero a septiembre)
- Evita duplicados verificando si el registro ya existe
- Crea automáticamente clientes, áreas, servicios y tareas necesarios

### 4. Verifica Totales
- Muestra totales antes y después de la importación
- Compara con objetivos del Excel
- Muestra diferencias

## Resultados Esperados

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| **Registros 2025** | ~34,350 | ~43,800 | +9,450 |
| **Horas Totales** | ~30,110 | ~39,290 | +9,180 |
| **Diferencia vs Excel** | **-25.5%** | **-2.8%** | ✅ **89% recuperado** |

### Por Cliente (Top diferencias restantes):
- FALABELLA: -6.1% (-327 horas)
- GUACOLDA: -8.2% (-153 horas)
- MAE: -7.0% (-81 horas)
- HITES: -12.1% (-98 horas)

El resto de clientes tienen diferencias < 5% ✅

## Verificación Post-Importación

Para verificar que los datos fueron importados correctamente:

1. **Acceder al dashboard de AgentTracker**
   ```
   https://agenttracker.onrender.com/dashboard
   ```

2. **Verificar clientes principales**
   - FALABELLA debería tener ~5,060 horas
   - Collahuasi: ~4,742 horas
   - CLÍNICAS: ~4,438 horas

3. **Verificar personas nuevas**
   - Ir a `/personas`
   - Buscar: María Marañón, Vicente Vera, Catalina Durán, etc.

## Troubleshooting

### Error: "DATABASE_URL no está configurada"
**Solución**: Render debería tener esta variable configurada automáticamente. Verifica en Dashboard > Environment.

### Error: "No se encuentra el archivo Excel"
**Solución**: Asegúrate de que `Historial 2024-2025.xlsx` esté en el mismo directorio que el script.

### Error: "NOT NULL constraint failed"
**Solución**: Este error ya fue corregido en el script `importar_horas_produccion.py`. Asegúrate de usar la versión más reciente del repo.

### El script tarda mucho
**Es normal**: Importar ~45,000 registros puede tomar 5-10 minutos. El script hace commits cada 5,000 registros.

## Notas Importantes

- ⚠️ **El script detecta duplicados**: Si lo ejecutas múltiples veces, no creará registros duplicados
- ✅ **Es seguro re-ejecutarlo**: Puedes correr el script varias veces sin problema
- 📊 **Los totales pueden variar ligeramente**: La diferencia de -2.8% es aceptable y puede deberse a redondeos o registros con datos incompletos en el Excel

## Contacto

Si tienes problemas ejecutando el script, contacta a:
- Desarrollador: [información de contacto]
- Documentación adicional: Ver `CLAUDE.md` en el repositorio
