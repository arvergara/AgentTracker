# Solución: Ingresos SPOT Sobredimensionados

## 🔍 Problema Identificado

Los ingresos de clientes SPOT están sobredimensionados debido a un **mapeo incorrecto** en el script `importar_ingresos_csv_final.py`.

### Causa Raíz

El archivo `importar_ingresos_csv_final.py` (líneas 16-29) contiene un mapeo que asigna clientes SPOT del CSV a clientes PERMANENTES existentes:

```python
MAPEO_CLIENTES = {
    'CAPITAL ADVISORES': 'Comité de Paltas',  # ❌ INCORRECTO
    'CAPSTONE': 'Capstone Copper',            # ❌ INCORRECTO
    'BCI': 'Grupo Defensa',                   # ❌ INCORRECTO
    'CONCHA Y TORO': 'Frutas de Chile',       # ❌ INCORRECTO
}
```

### Consecuencia

1. Un cliente permanente (ej: "Capstone Copper") tiene sus propios servicios e ingresos permanentes
2. El CSV de SPOT tiene un cliente "CAPSTONE" con proyectos puntuales
3. El script mapea "CAPSTONE" → "Capstone Copper"
4. **Resultado**: Los ingresos SPOT se suman a los ingresos permanentes del mismo cliente
5. El dashboard muestra: Ingresos Permanentes + Ingresos SPOT = **DUPLICACIÓN**

### Ejemplo Real del CSV

El archivo `Clientes_Spot.csv` tiene:

```csv
CAPSTONE;Diseño por 1 vez UF 70;;;;;;;;;;;;;;70;
CAPSTONE;Embajadores por 1 vez UF 65;;;;;;;;;;;;;;;;65;
CAPSTONE;Un taller de vocería UF 200;;;;;;;;;;;;;;;;;200;
```

- **CAPSTONE** (SPOT): 70 + 65 + 200 = **335 UF** en proyectos puntuales
- **Capstone Copper** (PERMANENTE): tiene sus propios ingresos mensuales

El script actual SUMA ambos incorrectamente.

---

## ✅ Solución

### Paso 1: Diagnóstico

Ejecutar el script de verificación en producción para confirmar el problema:

```bash
python verificar_duplicacion_clientes.py
```

Este script identificará:
- Clientes que tienen servicios permanentes Y spot
- Cuánto está sobredimensionado cada cliente
- Servicios duplicados a eliminar

### Paso 2: Limpieza de Datos Incorrectos

**⚠️ IMPORTANTE: Hacer backup de la base de datos antes de ejecutar**

1. **Modo simulación** (sin hacer cambios):
   ```bash
   python limpiar_servicios_spot_duplicados.py
   ```

2. **Revisar** los cambios propuestos

3. **Ejecutar limpieza** (con confirmación):
   ```bash
   python limpiar_servicios_spot_duplicados.py --ejecutar
   ```

Este script:
- ✓ Identifica servicios SPOT incorrectamente asignados a clientes permanentes
- ✓ Elimina los registros de `IngresoMensual` duplicados
- ✓ Desactiva los servicios SPOT incorrectos
- ✓ Actualiza registros de horas (si existen)

### Paso 3: Re-importación Correcta

Usar el script corregido que **NO mapea** clientes SPOT a permanentes:

```bash
python importar_ingresos_spot_corregido.py /ruta/a/Clientes_Spot.csv
```

Este script:
- ✓ Crea clientes SPOT independientes (no mapea a permanentes)
- ✓ Normaliza nombres sin cambiarlos a otros clientes
- ✓ Crea servicios por cada proyecto del CSV
- ✓ Asigna ingresos mensuales correctamente

### Paso 4: Verificación

Después de la corrección, verificar en el dashboard:

1. Los clientes SPOT deben aparecer como clientes independientes
2. Los ingresos permanentes no deben incluir ingresos spot
3. El total de ingresos SPOT debe coincidir con el CSV

---

## 📋 Scripts Creados

### 1. `verificar_duplicacion_clientes.py`
- **Propósito**: Diagnosticar el problema sin hacer cambios
- **Uso**: `python verificar_duplicacion_clientes.py`
- **Output**: Clientes con servicios permanentes y spot mezclados

### 2. `limpiar_servicios_spot_duplicados.py`
- **Propósito**: Eliminar servicios SPOT incorrectamente asignados
- **Uso**:
  - Simulación: `python limpiar_servicios_spot_duplicados.py`
  - Ejecutar: `python limpiar_servicios_spot_duplicados.py --ejecutar`
- **Acción**: Desactiva servicios, elimina ingresos duplicados

### 3. `importar_ingresos_spot_corregido.py`
- **Propósito**: Re-importar ingresos SPOT correctamente
- **Uso**: `python importar_ingresos_spot_corregido.py <csv_path>`
- **Acción**: Crea clientes SPOT independientes

### 4. `diagnostico_ingresos_spot_completo.py`
- **Propósito**: Análisis detallado de todos los ingresos spot
- **Uso**: `python diagnostico_ingresos_spot_completo.py`
- **Output**: Desglose completo por año, mes, cliente

---

## 🔧 Correcciones Aplicadas

### En `importar_ingresos_spot_corregido.py`

**ANTES (incorrecto):**
```python
MAPEO_CLIENTES = {
    'CAPSTONE': 'Capstone Copper',  # Mapea a cliente permanente
}
```

**DESPUÉS (correcto):**
```python
NORMALIZACION_NOMBRES = {
    'CAPSTONE': 'Capstone',  # Cliente SPOT independiente
}
```

### Diferencias Clave:
- ❌ Antes: Mapeaba a clientes existentes (permanentes)
- ✅ Ahora: Solo normaliza nombres sin cambiar la identidad del cliente
- ❌ Antes: Creaba servicios SPOT en clientes permanentes
- ✅ Ahora: Crea clientes SPOT independientes

---

## 📊 Impacto Esperado

### Antes de la Corrección:
```
Cliente: Capstone Copper (Permanente)
├── Servicios Permanentes: 5,000 UF
└── Servicios SPOT (duplicados): 335 UF
    TOTAL SOBREDIMENSIONADO: 5,335 UF ❌
```

### Después de la Corrección:
```
Cliente: Capstone Copper (Permanente)
└── Servicios Permanentes: 5,000 UF ✓

Cliente: Capstone (SPOT)
└── Servicios SPOT: 335 UF ✓

TOTAL CORRECTO: Separados correctamente
```

---

## ⚠️ Precauciones

1. **Backup**: Hacer backup de la base de datos antes de ejecutar limpieza
2. **Ambiente**: Probar primero en ambiente local/desarrollo
3. **Verificación**: Ejecutar scripts de diagnóstico antes y después
4. **Registros de horas**: El script de limpieza actualiza `servicio_id` a NULL en horas registradas en servicios spot eliminados

---

## 🚀 Ejecución en Producción (Render)

### Opción 1: Via Shell de Render

1. Acceder al shell de Render:
   - Dashboard → AgentTracker → Shell

2. Subir scripts:
   ```bash
   # Los scripts ya deberían estar en el repositorio
   ls -la *.py
   ```

3. Ejecutar secuencia:
   ```bash
   # Diagnóstico
   python verificar_duplicacion_clientes.py

   # Limpieza (simulación)
   python limpiar_servicios_spot_duplicados.py

   # Limpieza (ejecutar)
   python limpiar_servicios_spot_duplicados.py --ejecutar

   # Re-importación
   python importar_ingresos_spot_corregido.py Clientes_Spot.csv
   ```

### Opción 2: Conexión Directa a PostgreSQL

Si prefieres conectarte directamente a PostgreSQL:

```bash
# Obtener DATABASE_URL desde Render dashboard
export DATABASE_URL="postgresql://..."

# Ejecutar scripts localmente apuntando a producción
python limpiar_servicios_spot_duplicados.py --ejecutar
```

---

## 📝 Notas Adicionales

### Clientes que requieren atención

Según el CSV, estos clientes SPOT podrían estar mapeados incorrectamente:

- **BCI** → podría estar mapeado a "Grupo Defensa"
- **Capstone** → mapeado a "Capstone Copper"
- **Concha y Toro** → mapeado a "Frutas de Chile"
- **Capital Advisores** → mapeado a "Comité de Paltas"

Verificar si estos clientes deben ser independientes o si el mapeo es intencional.

### Estructura correcta del CSV

El CSV `Clientes_Spot.csv` tiene columnas:
1. Nombre del cliente (puede repetirse)
2. Descripción del servicio/proyecto
3. Meses: ene-24, feb-24, ..., dic-25

Múltiples filas con el mismo cliente son CORRECTAS (representan diferentes proyectos).

---

## ✉️ Soporte

Si encuentras algún problema durante la ejecución:

1. Revisa los logs de cada script
2. Verifica que la estructura del CSV no haya cambiado
3. Consulta los comentarios en el código de cada script

---

**Fecha de creación**: 2025-10-23
**Problema**: Ingresos SPOT sobredimensionados por mapeo incorrecto
**Estado**: Solución implementada y lista para aplicar
